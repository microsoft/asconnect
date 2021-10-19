"""Wrapper for altool."""

import enum
import logging
import subprocess
import time
from typing import Optional


class Platform(enum.Enum):
    """The platforms that altool supports."""

    IOS = "ios"
    MACOS = "osx"
    TVOS = "appletvos"


def _check_should_restart(line: str) -> bool:
    """Check if the line indicates that the upload should be re-run on failure.

    :param line: The output line to check

    :returns: True if it indicates a restart would help, False otherwise
    """

    for match in [
        "Error: Server returned an invalid MIME type: text/plain",
        "Error: The request timed out.",
    ]:
        if match in line:
            return True

    return False


def upload(
    *,
    ipa_path: str,
    platform: Platform,
    key_id: str,
    issuer_id: str,
    log: Optional[logging.Logger] = None,
    attempt: int = 1,
    max_attempts: int = 3,
) -> None:
    """Upload a build to app store connect.

    :param ipa_path: The path to the ipa to upload
    :param platform: The platform the app is for
    :param key_id: The ID for the key used for auth
    :param issuer_id: The ID of the issuer of the auth key
    :param log: Any base logger to be used (one will be created if not supplied)
    :param attempt: The attempt this is
    :param max_attempts: The number of attempts allowed

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

    upload_process = subprocess.Popen(  # pylint: disable=consider-using-with
        command,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )

    assert upload_process.stdout is not None
    command_output = ""
    should_restart = False
    for line in iter(upload_process.stdout.readline, ""):
        log.info(line.rstrip())
        if _check_should_restart(line):
            should_restart = True
        command_output += line
    upload_process.stdout.close()
    upload_process.wait()

    if upload_process.returncode == 0:
        return

    if should_restart and attempt < max_attempts:
        log.info("Upload failed due to intermittent issue. Will sleep for 1 minute and try again.")
        time.sleep(60)
        upload(
            ipa_path=ipa_path,
            platform=platform,
            key_id=key_id,
            issuer_id=issuer_id,
            log=log,
            attempt=attempt + 1,
            max_attempts=max_attempts,
        )
        return

    raise subprocess.CalledProcessError(
        upload_process.returncode,
        command,
        "Failed to upload the build. Please see the logs for more information.",
    )
