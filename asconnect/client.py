"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
from typing import Optional


from asconnect.httpclient import HttpClient
from asconnect.app_client import AppClient
from asconnect.app_info_client import AppInfoClient
from asconnect.beta_review_client import BetaReviewClient
from asconnect.build_client import BuildClient
from asconnect.screenshot_client import ScreenshotClient
from asconnect.users_client import UsersClient
from asconnect.version_client import VersionClient

# pylint: disable=too-many-public-methods


class Client:
    """Wrapper class around the ASC API."""

    log: logging.Logger
    http_client: HttpClient

    app: AppClient
    app_info: AppInfoClient
    beta_review: BetaReviewClient
    build: BuildClient
    screenshots: ScreenshotClient
    users: UsersClient
    version: VersionClient

    def __init__(
        self,
        *,
        key_id: str,
        key_contents: str,
        issuer_id: str,
        log: Optional[logging.Logger] = None,
    ) -> None:
        """Construct a new client object.

        :param key_id: The ID of your key (can be found in app store connect)
        :param key_contents: The contents of your key
        :param issuer_id: The contents of your key (can be found in app store connect
        :param log: Any base logger to be used (one will be created if not supplied)
        """

        if log is None:
            self.log = logging.getLogger("asconnect")
        else:
            self.log = log.getChild("asconnect")

        self.http_client = HttpClient(
            key_id=key_id, key_contents=key_contents, issuer_id=issuer_id, log=self.log
        )

        self.app = AppClient(http_client=self.http_client, log=self.log)
        self.app_info = AppInfoClient(http_client=self.http_client, log=self.log)
        self.beta_review = BetaReviewClient(http_client=self.http_client, log=self.log)
        self.build = BuildClient(http_client=self.http_client, log=self.log)
        self.screenshots = ScreenshotClient(http_client=self.http_client, log=self.log)
        self.users = UsersClient(http_client=self.http_client, log=self.log)
        self.version = VersionClient(http_client=self.http_client, log=self.log)
