"""Wrapper for iTMS tool."""

import logging
import os
import shutil
import subprocess
import tempfile
from typing import Optional


from asconnect.utilities import md5_file


def write_metadata(ipa_path: str, apple_id: str, itmsp_path: str) -> None:
    """Write out the metadata for an ITMS bundle.

    :param ipa_path: The path to the IPA
    :param apple_id: The Apple ID for the app (this is _not_ the app ID)
    :param itmsp_path: The path to the ITMS bundle
    """

    metadata = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://apple.com/itunes/importer" version="software5.4">
<software_assets apple_id="{apple_id}" app_platform="ios">
<asset type="bundle">
    <data_file>
    <size>{os.path.getsize(ipa_path)}</size>
    <file_name>{os.path.basename(ipa_path)}</file_name>
    <checksum type="md5">{md5_file(ipa_path)}</checksum>
    </data_file>
</asset>
</software_assets>
</package>
"""

    metadata_path = os.path.join(itmsp_path, "metadata.xml")
    with open(metadata_path, "w") as metadata_file:
        metadata_file.write(metadata)


def remove_upload_tokens() -> None:
    """Remove any existing upload tokens.

    If we don't remove these, we can get an error stating that there is already
    another upload process running. Xcode normally cleans these up, but since we
    are running directly, we have to do it.
    """
    token_path = os.path.expanduser("~")
    token_path = os.path.join(
        token_path, "Library", "Caches", "com.apple.amp.itmstransporter", "UploadTokens"
    )

    if not os.path.exists(token_path):
        return

    for token_file in os.listdir(token_path):
        token_file_path = os.path.join(token_path, token_file)
        os.remove(token_file_path)


def upload_build(
    *,
    ipa_path: str,
    bundle_id: str,
    app_id: str,
    username: str,
    password: str,
    log: Optional[logging.Logger] = None,
) -> None:
    """Upload a new build to ITC

    :param str ipa_path: The path to the .ipa file
    :param str bundle_id: The bundle ID for the app
    :param str app_id: The Apple ID for the app. This is _not_ the same as the app ID
    :param str username: The username to use for authentication
    :param str password: The password to use for authentication
    :param Optional[logging.Logger] log: An optional logger to use

    :raises CalledProcessError: If the upload does not complete successfully
    """

    if log:
        log = log.getChild(__name__)
    else:
        log = logging.getLogger(__name__)

    remove_upload_tokens()

    upload_dir = tempfile.mkdtemp()

    itmsp_path = os.path.join(upload_dir, f"{bundle_id}.itmsp")
    os.makedirs(itmsp_path)

    shutil.copy(ipa_path, itmsp_path)

    write_metadata(ipa_path, app_id, itmsp_path)

    command = [
        "xcrun",
        "iTMSTransporter",
        "-m",
        "upload",
        "-u",
        username,
        "-p",
        "@env:ITMS_TRANSPORTER_PASSWORD",
        "-f",
        itmsp_path,
        "-k",
        "100000",
    ]

    log.debug(f"Running itms upload: {command}")

    current_environment = os.environ.copy()
    current_environment["ITMS_TRANSPORTER_PASSWORD"] = password

    upload_process = subprocess.Popen(
        command,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        env=current_environment,
    )

    assert upload_process.stdout is not None
    command_output = ""
    for line in iter(upload_process.stdout.readline, ""):
        log.info(line.rstrip())
        command_output += line
    upload_process.stdout.close()
    upload_process.wait()

    if upload_process.returncode != 0:
        raise subprocess.CalledProcessError(
            upload_process.returncode,
            command,
            "Failed to upload the build. Please see the logs for more information.",
        )
