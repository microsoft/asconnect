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

        self.identifier = data.get("id", "<unknown>")
        self.status = int(data.get("status", -1))
        self.code = data.get("code", "<unknown>")
        self.title = data.get("title", "<unknown>")
        self.detail = data.get("detail", "<unknown>")
        self.source = data.get("source")

        super().__init__(f"[{self.status}] {self.title} ({self.code}): {self.detail}")
