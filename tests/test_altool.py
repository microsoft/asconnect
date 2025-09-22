"""Tests for altool parameter validation."""

import os
import subprocess


def test_altool_wrong_parameter() -> None:
    """Test that altool validates the correct parameter names."""

    print("Starting test...")

    key_id = os.getenv('ASC_KEY_ID', 'test_key_id')
    issuer_id = os.getenv('ASC_ISSUER_ID', 'test_issuer_id')

    result = subprocess.run([
        "xcrun", "altool",
        "--upload-app",
        "-f", "/nonexistent/file.ipa",
        "-t", "ios",
        "--apiKeyWrong", key_id,  # Wrong parameter name
        "--apiIssuer", issuer_id,  # Wrong parameter name
        "--verbose"
    ], capture_output=True, text=True, timeout=30, check=False)

    print(f"returncode: {result.returncode}")
    print(f"stderr: {result.stderr}")

    # Check that the error is about parameters, not just file not found
    error_text = result.stderr.lower()

    # If we get a file error instead of parameter error, the wrong parameters were accepted
    if "failed to load authkey file" in error_text and "expected api key argument is missing" not in error_text:
        assert False, f"Wrong parameters were accepted! Should have been rejected. Error: {result.stderr}"

    # If we get parameter error, that's good - wrong parameters were rejected
    if "expected api key argument is missing" in error_text:
        print("✓ Test passed: Wrong parameters were correctly rejected")
        return

    if result.returncode == 0:
        assert False, "Wrong parameters should cause altool to fail"

    assert False, f"Unexpected error with wrong parameters: {result.stderr}"


def test_altool_correct_parameters() -> None:
    """Test that altool accepts the correct parameter names."""

    print("Starting correct parameters test...")

    key_id = os.getenv('ASC_KEY_ID', 'test_key_id')
    issuer_id = os.getenv('ASC_ISSUER_ID', 'test_issuer_id')

    # Test with CORRECT parameter names (should fail due to missing file, not parameters)
    result = subprocess.run([
        "xcrun", "altool",
        "--upload-app",
        "-f", "/nonexistent/file.ipa",
        "-t", "ios",
        "--api-key", key_id,  # Correct parameter name
        "--api-issuer", issuer_id,  # Correct parameter name
        "--verbose"
    ], capture_output=True, text=True, timeout=30, check=False)

    print(f"returncode: {result.returncode}")
    print(f"stderr: {result.stderr}")

    # Check that the error is about file not found, not about wrong parameters
    error_text = result.stderr.lower()

    # If we get a file error, that's good - correct parameters were accepted
    if "failed to load authkey file" in error_text:
        print("✓ Test passed: Correct parameters were accepted (failed due to missing file)")
        return  # Test passes

    # If we get parameter error, that's bad - correct parameters were rejected
    if "expected api key argument is missing" in error_text:
        assert False, "Correct parameters should not cause parameter error"

    # If altool succeeded (returncode 0), that's unexpected but not necessarily bad
    if result.returncode == 0:
        print("✓ Test passed: Correct parameters were accepted (command succeeded)")
        return

    # Any other case is unexpected
    assert False, f"Unexpected error with correct parameters: {result.stderr}"


if __name__ == "__main__":
    test_altool_wrong_parameter()
    test_altool_correct_parameters()
