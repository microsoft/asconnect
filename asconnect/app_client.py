"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
from typing import Any, Dict, Iterator, List, Optional

from asconnect.httpclient import HttpClient
from asconnect.models import App, AppStoreVersion, Platform


class AppClient:
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
        self.log = log.getChild("app")

    def get_all(
        self,
        url: Optional[str] = None,
    ) -> Iterator[App]:
        """Get all apps.

        :param Optional[str] url: The URL to use (will be generated if not supplied)

        :returns: A list of apps
        """
        self.log.debug("Getting all apps...")
        url = self.http_client.generate_url("apps")
        yield from self.http_client.get(url=url, data_type=List[App])

    def get_from_bundle_id(self, bundle_id: str) -> Optional[App]:
        """Get a particular app.

        :param bundle_id: The bundle ID of the app to get

        :returns: The app if found, None otherwise
        """
        self.log.debug(f"Getting app with bundle id '{bundle_id}'...")
        for app in self.get_all():
            if app.bundle_id == bundle_id:
                return app
        return None

    def create_new_version(
        self,
        *,
        version: str,
        app_id: str,
        platform: Platform = Platform.IOS,
        copyright_text: Optional[str] = None,
        uses_idfa: Optional[bool] = None,
    ) -> AppStoreVersion:
        """Create a new version on the app store.

        :param version: The version to create
        :param app_id: The ID of the app
        :param platform: The platform this app is (defaults to iOS)
        :param copyright_text: The copyright string to use
        :param uses_idfa: Set to True if this app uses the advertising ID, false otherwise

        :raises AppStoreConnectError: On a failure response

        :returns: An AppStoreVersion
        """

        self.log.info(f"Creating version {version} for {app_id}...")

        attributes: Dict[str, Any] = {
            "platform": platform.value,
            "versionString": version,
            "releaseType": "MANUAL",  # TODO This should support scheduling
        }

        if copyright_text:
            attributes["copyright"] = copyright_text

        if uses_idfa is not None:
            attributes["usesIdfa"] = uses_idfa

        data = {
            "data": {
                "attributes": attributes,
                "type": "appStoreVersions",
                "relationships": {
                    "app": {
                        "data": {
                            "type": "apps",
                            "id": app_id,
                        }
                    }
                },
            }
        }

        self.log.debug(f"Creation data: {data}")

        return self.http_client.post(
            endpoint="appStoreVersions",
            data=data,
            data_type=AppStoreVersion,
        )
