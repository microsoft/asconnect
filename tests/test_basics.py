# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Tests for the package."""

import datetime
import os
import sys

import jwt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import asconnect  # pylint: disable=wrong-import-order


# pylint: disable=too-many-lines


def test_import() -> None:
    """Test that importing the package works."""
    assert asconnect is not None


def test_token(client: asconnect.Client) -> None:
    """Test the JWT token generation"""

    token = client.http_client.generate_token()

    decoded = jwt.decode(token, verify=False)
    assert decoded["iss"] == client.http_client.issuer_id
    assert decoded["aud"] == "appstoreconnect-v1"
    assert datetime.datetime.fromtimestamp(
        decoded["exp"]
    ) < datetime.datetime.now() + datetime.timedelta(minutes=20)

    # Ensure we return the cached version
    token2 = client.http_client.generate_token()
    assert token == token2
