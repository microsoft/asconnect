"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
from typing import Any, Dict, Iterator, List, Optional

from asconnect.httpclient import HttpClient

from asconnect.models import (
    BetaAppLocalization,
    BetaAppReviewDetail,
    BetaBuildLocalization,
    BetaGroup,
)


class BetaReviewClient:
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
        self.log = log.getChild("beta_review")

    def set_beta_app_review_details(
        self,
        *,
        app_id: str,
        contact_email: str,
        contact_first_name: str,
        contact_last_name: str,
        contact_phone: str,
        demo_account_name: Optional[str] = None,
        demo_account_password: Optional[str] = None,
        demo_account_required: Optional[bool] = None,
        notes: Optional[str] = None,
    ) -> BetaAppReviewDetail:
        """Set the Beta app review details.

        :param str app_id: The Apple ID for the app
        :param str contact_email: The email for the app review contact
        :param str contact_first_name: The first name for the app review contact
        :param str contact_last_name: The last name for the app review contact
        :param str contact_phone: The phone number for the app review contact
        :param Optional[str] demo_account_name: The username for the demo account
        :param Optional[str] demo_account_password: The password for the demo account
        :param Optional[bool] demo_account_required: Set to True to mark the demo account as required
        :param Optional[str] notes: Any notes for the reviewer

        :returns: The raw response
        """

        self.log.info(f"Setting beta app review details on {app_id}")

        attributes: Dict[str, Any] = {
            "contactEmail": contact_email,
            "contactFirstName": contact_first_name,
            "contactLastName": contact_last_name,
            "contactPhone": contact_phone,
        }

        if demo_account_name is not None:
            attributes["demoAccountName"] = demo_account_name

        if demo_account_password is not None:
            attributes["demoAccountPassword"] = demo_account_password

        if demo_account_required is not None:
            attributes["demoAccountRequired"] = demo_account_required

        if notes is not None:
            attributes["notes"] = notes

        body = {"data": {"attributes": attributes, "id": app_id, "type": "betaAppReviewDetails"}}

        self.log.debug(f"Beta review details: {body}")

        return self.http_client.patch(
            endpoint=f"betaAppReviewDetails/{app_id}", data=body, data_type=BetaAppReviewDetail
        )

    def get_beta_app_localizations(self, app_id: str) -> Iterator[BetaAppLocalization]:
        """Get the beta app localizations.

        :param app_id: The apple identifier for the app to get the localizations for

        :returns: An iterator to the beta app localizations
        """
        self.log.debug(f"Getting beta app localizations for {app_id}")
        url = self.http_client.generate_url(f"apps/{app_id}/betaAppLocalizations")
        yield from self.http_client.get(url=url, data_type=List[BetaAppLocalization])

    def get_beta_build_localizations(self, build_id: str) -> Iterator[BetaBuildLocalization]:
        """Get the beta app localizations.

        :param build_id: The identifier for the build to get the localizations for

        :returns: An iterator to the beta app localizations
        """
        self.log.debug(f"Getting beta build localizations for {build_id}")
        url = self.http_client.generate_url(f"betaBuildLocalizations?filter[build]={build_id}")
        yield from self.http_client.get(url=url, data_type=List[BetaBuildLocalization])

    def set_beta_app_localizations(
        self, app_id: str, localizations: Dict[str, Dict[str, str]]
    ) -> None:
        """Set the app localizations.

        :param app_id: The apple identifier for the app to set the localizations for
        :param localizations: A dictionary of language codes to localization attributes
        """

        self.log.info(f"Setting beta app localizations for {app_id}")

        existing_localizations = {}

        for localization in self.get_beta_app_localizations(app_id):
            existing_localizations[localization.attributes.locale] = localization

        for language_code, language_info in localizations.items():
            self.log.debug(f"Setting localizations for {language_code}: {language_info}")
            existing_localization = existing_localizations.get(language_code)

            self.log.debug(f"Existing localization: {existing_localization}")

            if existing_localization:
                self.http_client.patch(
                    endpoint=f"betaAppLocalizations/{existing_localization.identifier}",
                    data={
                        "data": {
                            "attributes": language_info,
                            "id": existing_localization.identifier,
                            "type": "betaAppLocalizations",
                        }
                    },
                    data_type=BetaAppLocalization,
                )
            else:
                language_info["locale"] = language_code
                self.http_client.post(
                    endpoint="betaAppLocalizations",
                    data={
                        "data": {
                            "attributes": language_info,
                            "type": "betaAppLocalizations",
                            "relationships": {
                                "app": {
                                    "data": {
                                        "type": "apps",
                                        "id": app_id,
                                    }
                                }
                            },
                        }
                    },
                )

    def set_whats_new_for_build(self, build_id: str, localizations: Dict[str, str]) -> None:
        """Set the whats new for a build.

        :param build_id: The apple identifier for the app to set the localizations for
        :param localizations: A dictionary of language codes to localization info
        """

        self.log.info(f"Setting whats new for build {build_id}")
        self.log.debug(f"Localizations: {localizations}")

        existing_localizations = {}

        for localization in self.get_beta_build_localizations(build_id):
            existing_localizations[localization.attributes.locale] = localization

        self.log.debug(f"Existing localizations: {existing_localizations}")

        for language_code, whats_new in localizations.items():
            self.log.debug(f"Setting localization for {language_code}")
            attributes = {"whatsNew": whats_new}

            existing_localization = existing_localizations.get(language_code)

            if existing_localization:
                self.http_client.patch(
                    endpoint=f"betaBuildLocalizations/{existing_localization.identifier}",
                    data={
                        "data": {
                            "attributes": attributes,
                            "id": existing_localization.identifier,
                            "type": "betaBuildLocalizations",
                        }
                    },
                    data_type=BetaBuildLocalization,
                )
            else:
                attributes["locale"] = language_code
                self.http_client.post(
                    endpoint="betaBuildLocalizations",
                    data={
                        "data": {
                            "attributes": attributes,
                            "type": "betaBuildLocalizations",
                            "relationships": {
                                "build": {
                                    "data": {
                                        "type": "builds",
                                        "id": build_id,
                                    }
                                }
                            },
                        }
                    },
                )

    def get_beta_groups(self, app_id: str) -> Iterator[BetaGroup]:
        """Get the beta groups

        :param app_id: The ID of the app to filter on

        :returns: An iterator to the beta groups
        """
        self.log.debug(f"Getting beta groups for {app_id}")
        url = self.http_client.generate_url(f"betaGroups?filter[app]={app_id}")
        yield from self.http_client.get(url=url, data_type=List[BetaGroup])

    def set_beta_groups_on_build(self, build_id: str, beta_groups: List[BetaGroup]) -> None:
        """Set the Beta groups on a build.

        :param build_id: The build ID for the build to set the groups on
        :param beta_groups: The groups to add
        """
        self.log.info(f"Setting beta groups on {build_id}: {beta_groups}")

        data = []
        for beta_group in beta_groups:
            data.append({"type": "betaGroups", "id": beta_group.identifier})

        body = {"data": data}

        self.http_client.post(endpoint=f"builds/{build_id}/relationships/betaGroups", data=body)

    def submit_for_beta_review(self, build_id: str) -> None:
        """Submit a build for beta review

        :param build_id: The build ID for the build to set the groups on
        """

        self.log.info(f"Submitting build for beta review: {build_id}")

        body = {
            "data": {
                "type": "betaAppReviewSubmissions",
                "relationships": {
                    "build": {
                        "data": {
                            "id": build_id,
                            "type": "builds",
                        }
                    }
                },
            }
        }

        self.log.debug(f"Data: {body}")

        self.http_client.post(endpoint="betaAppReviewSubmissions", data=body)
