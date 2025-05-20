"""Configuration for tests."""

import json
import os
import subprocess
import sys

import _pytest
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import asconnect  # pylint: disable=wrong-import-order


def pytest_configure(config: _pytest.config.Config) -> None:  # type: ignore
    """Run configuration before tests.

    :param config: The pytest config object
    """
    _ = config

    repo_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        universal_newlines=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()

    env_file_path = os.path.join(repo_root, ".env")

    if not os.path.exists(env_file_path):
        return

    with open(env_file_path, "r", encoding="utf-8") as env_file:
        contents = env_file.read()

    for line in contents.split("\n"):
        if len(line) == 0:
            continue
        name, value = line.split("=")
        os.environ[name] = value


def get_test_data() -> tuple[str, str, str]:
    """Get the test data.

    :returns: The test data
    """
    tests_path = os.path.dirname(os.path.abspath(__file__))
    test_data_path = os.path.join(tests_path, "test_data.json")
    with open(test_data_path, "r", encoding="utf-8") as test_data_file:
        all_test_data = json.load(test_data_file)

    test_data = all_test_data["base"]

    return test_data["key_id"], test_data["key"], test_data["issuer_id"]


@pytest.fixture(scope="session")
def client() -> asconnect.Client:
    """Get the test client.

    :returns: The test client
    """
    key_id, key, issuer_id = get_test_data()

    return asconnect.Client(key_id=key_id, key_contents=key, issuer_id=issuer_id)


@pytest.fixture(scope="session")
def app_id() -> str:
    """Get the test app ID.

    :returns: The test app ID
    """
    return ""
