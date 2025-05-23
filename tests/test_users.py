# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Tests for the package."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import asconnect  # pylint: disable=wrong-import-order


def test_get_users(client: asconnect.Client) -> None:
    """Test that we can upload all screenshots."""

    users = list(client.users.get_users())

    assert len(users) > 0
