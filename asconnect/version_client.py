"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
from typing import Iterator, List, Optional

from asconnect.httpclient import HttpClient
from asconnect.models import (
    AppStoreVersion,
    AppStoreVersionPhasedRelease,
    PhasedReleaseState,
    Platform,
    AppStoreVersionLocalization,
    AppStoreReviewDetails,
    IdfaDeclaration,
)
from asconnect.utilities import next_or_none, update_query_parameters


class VersionClient:
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
        self.log = log.getChild("version")

    def get(
        self,
        *,
        version_id: str,
    ) -> Optional[AppStoreVersion]:
        """Get the version with the given ID

        :param version_id: The version ID to get

        :returns: An AppStoreVersion if found, None otherwise
        """
        self.log.debug(f"Getting version {version_id}")
        url = self.http_client.generate_url(f"appStoreVersions/{version_id}")

        return next_or_none(self.http_client.get(url=url, data_type=AppStoreVersion))

    def get_all(
        self,
        *,
        app_id: str,
        version_string: Optional[str] = None,
        platform: Optional[Platform] = None,
    ) -> Iterator[AppStoreVersion]:
        """Get the versions for an app.

        :param app_id: The app ID to get the versions for
        :param version_string: The version to filter on (if any)
        :param platform: The platform to filter on (if any)

        :returns: An iterator to AppStoreVersion
        """
        self.log.info(f"Getting all versions of {app_id}...")
        self.log.debug(f"Version string: {version_string}")
        self.log.debug(f"Platform: {platform}")

        url = self.http_client.generate_url(f"apps/{app_id}/appStoreVersions")

        query_parameters = {}

        if version_string:
            query_parameters["filter[versionString]"] = version_string

        if platform:
            query_parameters["filter[platform]"] = platform.value

        url = update_query_parameters(url, query_parameters)

        yield from self.http_client.get(url=url, data_type=List[AppStoreVersion])

    def get_version(self, *, app_id: str, version_string: str) -> Optional[AppStoreVersion]:
        """Get the versions for an app.

        :param app_id: The app ID to get the version for
        :param version_string: The version string to get the version for

        :returns: An AppStoreVersion
        """
        self.log.info(f"Getting version {version_string} of {app_id}")
        return next_or_none(self.get_all(app_id=app_id, version_string=version_string))

    def get_phased_release(
        self,
        *,
        version_id: str,
    ) -> Optional[AppStoreVersionPhasedRelease]:
        """Get the phased release of given app version

        :param version_id: The version ID to query for phased releases

        :returns: An AppStoreVersionPhasedRelease if found, None otherwise
        """
        self.log.debug(f"Getting phased release of {version_id}")
        url = self.http_client.generate_url(
            f"appStoreVersions/{version_id}/appStoreVersionPhasedRelease"
        )

        return next_or_none(self.http_client.get(url=url, data_type=AppStoreVersionPhasedRelease))

    def create_phased_release(
        self,
        *,
        version_id: str,
        phased_release_state: PhasedReleaseState = PhasedReleaseState.INACTIVE,
    ) -> Optional[AppStoreVersionPhasedRelease]:
        """Create a phased release for a given app version, defaulting to creating an inactive release.

        :param version_id: The version ID to query for phased releases
        :param phased_release_state: the state of the initial rollout

        :returns: An AppStoreVersionPhasedRelease if found, None otherwise
        """

        self.log.info(f"Creating phased release ({phased_release_state}) for version {version_id}")

        return self.http_client.post(
            endpoint="appStoreVersionPhasedReleases",
            data={
                "data": {
                    "attributes": {"phasedReleaseState": phased_release_state.value},
                    "type": "appStoreVersionPhasedReleases",
                    "relationships": {
                        "appStoreVersion": {"data": {"id": version_id, "type": "appStoreVersions"}}
                    },
                }
            },
            data_type=AppStoreVersionPhasedRelease,
        )

    def delete_phased_release(
        self,
        *,
        phased_release_id: str,
    ) -> None:
        """Delete a Phased Release

        :param phased_release_id: The ID of the release set to delete

        :raises AppStoreConnectError: On failure to delete"""

        self.log.info(f"Deleting phased release: {phased_release_id}")
        self.http_client.delete(url=f"appStoreVersionPhasedReleases/{phased_release_id}")

    def patch_phased_release(
        self,
        *,
        phased_release_id: str,
        phased_release_state: PhasedReleaseState = PhasedReleaseState.INACTIVE,
    ) -> Optional[AppStoreVersionPhasedRelease]:
        """Update a Phased Release

        :param phased_release_id: The ID of the release set to modify
        :param phased_release_state: The state of the phased release to transition to

        :returns: The modified AppStoreVersionPhasedRelease

        """
        self.log.info(
            f"Patching phased release {phased_release_id} to state {phased_release_state}"
        )
        return self.http_client.patch(
            endpoint=f"appStoreVersionPhasedReleases/{phased_release_id}",
            data={
                "data": {
                    "attributes": {"phasedReleaseState": phased_release_state.value},
                    "type": "appStoreVersionPhasedReleases",
                    "id": phased_release_id,
                }
            },
            data_type=AppStoreVersionPhasedRelease,
        )

    def get_localizations(self, *, version_id: str) -> Iterator[AppStoreVersionLocalization]:
        """Get the version localizations for an app version.

        :param version_id: The version ID to get the localizations for

        :returns: An AppStoreVersion
        """
        self.log.info("Getting localizations for version {version_id}...")
        url = self.http_client.generate_url(
            f"appStoreVersions/{version_id}/appStoreVersionLocalizations"
        )
        yield from self.http_client.get(url=url, data_type=List[AppStoreVersionLocalization])

    def set_build(self, *, version_id: str, build_id: str) -> None:
        """Set the build for a version

        :param version_id: The ID of the version to set the build on
        :param build_id: The ID of the build to set
        """

        self.log.info(f"Setting build {build_id} for version {version_id}")

        self.http_client.patch(
            endpoint=f"appStoreVersions/{version_id}/relationships/build",
            data={
                "data": {
                    "type": "builds",
                    "id": build_id,
                }
            },
            data_type=None,
        )

    def get_app_review_details(self, *, version_id: str) -> Optional[AppStoreReviewDetails]:
        """Get the app review details for the version.

        :param version_id: The version ID to get the app review details for

        :returns: The app review details if set, None otherwise
        """
        self.log.debug(f"Getting app review details for version {version_id}")
        return next_or_none(
            self.http_client.get(
                endpoint=f"appStoreVersions/{version_id}/appStoreReviewDetail",
                data_type=AppStoreReviewDetails,
            )
        )

    def set_app_review_details(
        self,
        *,
        version_id: str,
        contact_email: str,
        contact_first_name: str,
        contact_last_name: str,
        contact_phone: str,
        demo_account_name: str,
        demo_account_password: str,
        demo_account_required: bool,
        notes: str,
    ) -> AppStoreReviewDetails:
        """Set the app store review details

        :param version_id: The ID of the version to set the build on
        :param contact_email: The email for the app review contact
        :param contact_first_name: The first name for the app review contact
        :param contact_last_name: The last name for the app review contact
        :param contact_phone: The phone number for the app review contact
        :param demo_account_name: The username for the demo account
        :param demo_account_password: The password for the demo account
        :param demo_account_required: Set to True to mark the demo account as required
        :param notes: Any notes for the reviewer

        :returns: The review details
        """

        self.log.info(f"Setting app review details for version {version_id}")

        existing_details = self.get_app_review_details(version_id=version_id)

        attributes = {
            "contactFirstName": contact_first_name,
            "contactLastName": contact_last_name,
            "contactPhone": contact_phone,
            "contactEmail": contact_email,
            "demoAccountName": demo_account_name,
            "demoAccountPassword": demo_account_password,
            "demoAccountRequired": demo_account_required,
            "notes": notes,
        }

        self.log.debug(f"Attributes: {attributes}")

        if existing_details:
            return self.http_client.patch(
                endpoint=f"appStoreReviewDetails/{existing_details.identifier}",
                data={
                    "data": {
                        "type": "appStoreReviewDetails",
                        "id": existing_details.identifier,
                        "attributes": attributes,
                    }
                },
                data_type=AppStoreReviewDetails,
            )

        return self.http_client.post(
            endpoint="appStoreReviewDetails",
            data={
                "data": {
                    "type": "appStoreReviewDetails",
                    "attributes": attributes,
                    "relationships": {
                        "appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}
                    },
                }
            },
            data_type=AppStoreReviewDetails,
        )

    def get_idfa(self, *, version_id: str) -> Optional[IdfaDeclaration]:
        """Get the advertising ID declaration.

        :param version_id: The version to get the declaration for

        :returns: The declaration if set, None otherwise
        """
        self.log.info(f"Getting current IDFA for version {version_id}")
        return next_or_none(
            self.http_client.get(
                endpoint=f"appStoreVersions/{version_id}/idfaDeclaration",
                data_type=IdfaDeclaration,
            )
        )

    def set_idfa(
        self,
        *,
        version_id: str,
        attributes_action_with_previous_ad: bool,
        attributes_app_installation_to_previous_ad: bool,
        honors_limited_ad_tracking: bool,
        serves_ads: bool,
    ) -> IdfaDeclaration:
        """Set the IDFA declaration

        :param version_id: The ID of the version to set the build on
        :param attributes_action_with_previous_ad: Set to True if the ID is used to attribute actions with a previous ad
        :param attributes_app_installation_to_previous_ad: Set to True if the ID is used to attribute an installation with a previous ad
        :param honors_limited_ad_tracking: Set to True to confirm that your app honors a users ad tracking preferences
        :param serves_ads: Set to True if the advertising ID will be used to serve ads within your app

        :returns: The review details
        """

        self.log.info(f"Setting IDFA for version {version_id}")

        existing_details = self.get_idfa(version_id=version_id)

        attributes = {
            "attributesActionWithPreviousAd": attributes_action_with_previous_ad,
            "attributesAppInstallationToPreviousAd": attributes_app_installation_to_previous_ad,
            "honorsLimitedAdTracking": honors_limited_ad_tracking,
            "servesAds": serves_ads,
        }

        self.log.debug(f"Attributes: {attributes}")

        if existing_details:
            self.log.debug("Patching existing IDFA")
            return self.http_client.patch(
                endpoint=f"idfaDeclarations/{existing_details.identifier}",
                data={
                    "data": {
                        "type": "idfaDeclarations",
                        "id": existing_details.identifier,
                        "attributes": attributes,
                    }
                },
                data_type=IdfaDeclaration,
            )

        self.log.debug("Setting new IDFA")
        return self.http_client.post(
            endpoint="idfaDeclarations",
            data={
                "data": {
                    "type": "idfaDeclarations",
                    "attributes": attributes,
                    "relationships": {
                        "appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}
                    },
                }
            },
            data_type=IdfaDeclaration,
        )

    def set_uses_idfa(
        self,
        *,
        version_id: str,
    ) -> AppStoreVersion:
        """Set that the app version uses an IDFA

        Note: This is a workaround due to the fact that setting this property
        when creating the app fails.

        :param version_id: The ID of the version to set the build on

        :returns: The IDFA details
        """

        self.log.info(f"Setting uses IDFA for version {version_id}")

        return self.http_client.patch(
            endpoint=f"appStoreVersions/{version_id}",
            data={
                "data": {
                    "type": "appStoreVersions",
                    "id": version_id,
                    "attributes": {"usesIdfa": True},
                }
            },
            data_type=AppStoreVersion,
        )

    def submit_for_review(
        self,
        *,
        version_id: str,
    ) -> None:
        """Submit the version for review

        :param version_id: The ID of the version to submit for review
        """

        self.log.info(f"Submitting version for review {version_id}")

        self.http_client.post(
            endpoint="appStoreVersionSubmissions",
            data={
                "data": {
                    "type": "appStoreVersionSubmissions",
                    "relationships": {
                        "appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}
                    },
                }
            },
            data_type=None,
        )
