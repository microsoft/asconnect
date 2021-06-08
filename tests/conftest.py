"""Configuration for tests."""

import os
import subprocess

import _pytest


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

    with open(env_file_path) as env_file:
        contents = env_file.read()

    for line in contents.split("\n"):
        if len(line) == 0:
            continue
        name, value = line.split("=")
        os.environ[name] = value
