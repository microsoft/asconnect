# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Tests for the package."""

import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import asconnect  # pylint: disable=wrong-import-order


# pylint: disable=too-many-lines


def test_get_builds(client: asconnect.Client) -> None:
    """Test get apps."""

    builds = client.build.get_builds()
    assert builds is not None


def test_get_builds_by_version(client: asconnect.Client, app_id: str) -> None:
    """Test get build by version."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None
    builds = next(client.build.get_builds(app_id=app.identifier))
    assert builds is not None


def test_upload(client: asconnect.Client) -> None:
    """Test that we can upload a build."""

    client.build.upload(
        ipa_path="",
        platform=asconnect.Platform.IOS,
    )


def test_wait_for_build(client: asconnect.Client, app_id: str) -> None:
    """Test that we can wait for a build."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    client.build.wait_for_build_to_process(app_id, "")


def test_get_build_beta_detail(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get a builds beta details."""

    build = client.build.get_from_build_number(build_number="", bundle_id=app_id)

    assert build is not None

    build_detail = client.build.get_beta_detail(build)

    assert build_detail is not None


def test_altool_parameter_validation() -> None:
    """Test that altool validates the correct parameter names."""

    key_id = os.getenv('ASC_KEY_ID', 'test_key_id')
    issuer_id = os.getenv('ASC_ISSUER_ID', 'test_issuer_id')

    # Test with WRONG parameter names (should fail)
    result = subprocess.run([
        "xcrun", "altool",
        "--upload-app",
        "-f", "/nonexistent/file.ipa",
        "-t", "ios",
        "--apiKeywrong", key_id,  # Wrong parameter name
        "--apiIssuer", issuer_id,  # Wrong parameter name
        "--verbose"
    ], capture_output=True, text=True, timeout=30)

    # Check that the error is about parameters, not just file not found
    error_text = result.stderr.lower()

    # If we get a file error instead of parameter error, the wrong parameters were accepted
    if "failed to load authkey file" in error_text and "expected api key argument is missing" not in error_text:
        raise AssertionError(f"Wrong parameters were accepted! Should have been rejected. Error: {result.stderr}")

    # If we get parameter error, that's good - wrong parameters were rejected
    if "expected api key argument is missing" in error_text:
        return  # Test passes

    # If altool succeeded (returncode 0), that's bad - wrong parameters were accepted
    if result.returncode == 0:
        raise AssertionError("Wrong parameters should cause altool to fail")

    # Any other case is unexpected
    raise AssertionError(f"Unexpected error with wrong parameters: {result.stderr}")
