"""Exceptions"""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Any


class AppStoreConnectError(Exception):
    """An error response from the API."""

    identifier: str
    code: str
    status: int
    title: str
    detail: str
    source: Any

    def __init__(self, data: Any):
        """Create a new instance.

        :param data: The raw data from the response

        :raises ValueError: If we can't decode the data
        """

        if not isinstance(data, dict):
            raise ValueError(f"Could not decode App Store Connect error: {data}")

        data = data["errors"]

        if not isinstance(data, list):
            raise ValueError(f"Could not decode App Store Connect error: {data}")

        data = data[0]

        self.identifier = data["id"]
        self.status = int(data["status"])
        self.code = data["code"]
        self.title = data["title"]
        self.detail = data["detail"]
        self.source = data.get("source")

        super().__init__(f"[{self.status}] {self.title} ({self.code}): {self.detail}")
