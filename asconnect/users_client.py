"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
from typing import Iterator, List

from asconnect.httpclient import HttpClient

from asconnect.models import User
from asconnect.utilities import update_query_parameters


class UsersClient:
    """Wrapper class around the ASC API."""

    log: logging.Logger
    http_client: HttpClient

    def __init__(
        self,
        *,
        http_client: HttpClient,
        log: logging.Logger,
    ) -> None:
        """Construct a new client object.

        :param http_client: The API HTTP client
        :param log: Any base logger to be used (one will be created if not supplied)
        """

        self.http_client = http_client
        self.log = log.getChild("users")

    def get_users(self) -> Iterator[User]:
        """Get all users.

        :returns: A list of users
        """

        self.log.info("Getting users...")

        url = self.http_client.generate_url("users")

        query_parameters = {"limit": "200"}

        url = update_query_parameters(url, query_parameters)

        yield from self.http_client.get(url=url, data_type=List[User])
