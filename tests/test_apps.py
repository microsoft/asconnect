# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Tests for the package."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import asconnect  # pylint: disable=wrong-import-order


# pylint: disable=too-many-lines


def test_get_apps(client: asconnect.Client) -> None:
    """Test get apps."""

    apps = list(client.app.get_all())
    assert len(apps) != 0
    print(apps[0])


def test_get_app(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get an app."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None


def test_get_attached_build(client: asconnect.Client, app_id: str) -> None:
    """Test get attached build."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    build = client.version.get_attached_build(version_id=version.identifier)
    assert build is not None


def test_create_new_version(client: asconnect.Client, app_id: str) -> None:
    """Test that we can create a new app store version."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    client.app.create_new_version(version="1.2.3", app_id=app.identifier)
