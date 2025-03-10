"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
from typing import Iterator

from asconnect.httpclient import HttpClient
from asconnect.models import AppInfoLocalization, AppInfo, AppStoreVersionLocalization
from asconnect.utilities import update_query_parameters


class AppInfoClient:
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
        self.log = log.getChild("appinfo")

    def get_app_info(self, *, app_id: str) -> list[AppInfo]:
        """Get the app info for an app.

        If there are two, one will be marked as ready for sale, the other will
        be one that is being prepared.

        :param app_id: The app ID to get the info for

        :returns: A list to AppInfoLocalization
        """
        self.log.debug(f"Getting app info for {app_id}")
        url = self.http_client.generate_url(f"apps/{app_id}/appInfos")

        return list(self.http_client.get(url=url, data_type=list[AppInfo]))

    def get_localizations(
        self,
        *,
        app_info_id: str,
        locale: str | None = None,
    ) -> Iterator[AppInfoLocalization]:
        """Get the app info for an app.

        :param app_info_id: The app info ID to get the localized info for
        :param locale: The version to filter on (if any)

        :returns: An iterator to AppInfoLocalization
        """

        self.log.debug(f"Getting localizations for {app_info_id} (locale={locale})")
        url = self.http_client.generate_url(f"appInfos/{app_info_id}/appInfoLocalizations")

        query_parameters = {}

        if locale:
            query_parameters["filter[locale]"] = locale

        url = update_query_parameters(url, query_parameters)

        yield from self.http_client.get(url=url, data_type=list[AppInfoLocalization])

    def set_localization_properties(
        self,
        *,
        localization_id: str,
        name: str | None = None,
        privacy_policy_text: str | None = None,
        privacy_policy_url: str | None = None,
        subtitle: str | None = None,
    ) -> AppInfoLocalization:
        """Set the properties on an app info localization

        Any left as None will be ignored.

        :param localization_id: The ID of the localization to patch
        :param name: The name of the app
        :param privacy_policy_text: The text of the privacy policy
        :param privacy_policy_url: The URL of the privacy policy
        :param subtitle: The sub-title for the app

        :returns: The new updated app info localization
        """

        self.log.info("Setting localization properties")

        attributes = {}

        if name:
            attributes["name"] = name

        if privacy_policy_text:
            attributes["privacyPolicyText"] = privacy_policy_text

        if privacy_policy_url:
            attributes["privacyPolicyUrl"] = privacy_policy_url

        if subtitle:
            attributes["subtitle"] = subtitle

        data = {
            "data": {
                "attributes": attributes,
                "type": "appInfoLocalizations",
                "id": localization_id,
            }
        }

        self.log.debug(f"Localization properties: {data}")

        return self.http_client.patch(
            endpoint=f"appInfoLocalizations/{localization_id}",
            data=data,
            data_type=AppInfoLocalization,
        )

    def set_localization_version_properties(
        self,
        *,
        version_localization_id: str,
        description: str | None = None,
        keywords: str | None = None,
        marketing_url: str | None = None,
        promotional_text: str | None = None,
        support_url: str | None = None,
        whats_new: str | None = None,
    ) -> AppInfoLocalization:
        """Set the properties on an app version localization

        Any left as None will be ignored.

        :param version_localization_id: The ID of the localization to patch
        :param description: The description for the app store
        :param keywords: The keywords for the app (comma separated)
        :param marketing_url: The marketing URL
        :param promotional_text: Any promotional text (can be set after submission)
        :param support_url: The support URL
        :param whats_new: The What's New text for the version (release notes)

        :returns: The new updated app version localization
        """

        self.log.info("Setting localization version properties")

        attributes = {}

        if description:
            attributes["description"] = description

        if keywords:
            attributes["keywords"] = keywords

        if marketing_url:
            attributes["marketingUrl"] = marketing_url

        if promotional_text:
            attributes["promotionalText"] = promotional_text

        if support_url:
            attributes["supportUrl"] = support_url

        if whats_new:
            attributes["whatsNew"] = whats_new

        data = {
            "data": {
                "attributes": attributes,
                "type": "appStoreVersionLocalizations",
                "id": version_localization_id,
            }
        }

        self.log.debug(f"Localization version properties: {data}")

        return self.http_client.patch(
            endpoint=f"appStoreVersionLocalizations/{version_localization_id}",
            data=data,
            data_type=AppStoreVersionLocalization,
        )
