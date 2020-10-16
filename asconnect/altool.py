"""Wrapper for altool."""

import enum
import logging
import subprocess
from typing import Optional


class Platform(enum.Enum):
    """The platforms that altool supports."""

    ios = "ios"
    macos = "osx"
    tvos = "appletvos"


def upload(
    *,
    ipa_path: str,
    platform: Platform,
    key_id: str,
    issuer_id: str,
    log: Optional[logging.Logger] = None,
) -> None:
    """Upload a build to app store connect.

    :param ipa_path: The path to the ipa to upload
    :param platform: The platform the app is for
    :param key_id: The ID for the key used for auth
    :param issuer_id: The ID of the issuer of the auth key
    :param log: Any base logger to be used (one will be created if not supplied)

    :raises CalledProcessError: If something goes wrong during upload
    """

    if log:
        log = log.getChild(__name__)
    else:
        log = logging.getLogger(__name__)

    command = [
        "xcrun",
        "altool",
        "--upload-app",
        "-f",
        ipa_path,
        "-t",
        platform.value,
        "-apiKey",
        key_id,
        "--apiIssuer",
        issuer_id,
    ]

    log.info(
        "Beginning upload. This can take a while and will not show any output while in progress."
    )

    upload_process = subprocess.Popen(
        command,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
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
