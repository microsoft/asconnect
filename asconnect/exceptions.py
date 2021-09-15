"""Exceptions"""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Any

import requests


class AppStoreConnectError(Exception):
    """An error response from the API."""

    identifier: str
    code: str
    status: int
    title: str
    detail: str
    source: Any
    response: requests.Response

    def __init__(self, response: requests.Response):
        """Create a new instance.

        :param response: The HTTP response

        :raises ValueError: If we can't decode the data
        """

        self.response = response

        data = response.json()

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
