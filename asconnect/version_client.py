"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
import time
from typing import Iterator

from asconnect.exceptions import AppStoreConnectError
from asconnect.httpclient import HttpClient
from asconnect.models import (
    AppStoreReviewDetails,
    AppStoreVersion,
    AppStoreVersionLocalization,
    AppStoreVersionPhasedRelease,
    Build,
    IdfaDeclaration,
    PhasedReleaseState,
    Platform,
    ReviewSubmission,
    ReviewSubmissionItem,
    ReviewSubmissionState,
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
    ) -> AppStoreVersion | None:
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
        version_string: str | None = None,
        platform: Platform | None = None,
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

        yield from self.http_client.get(url=url, data_type=list[AppStoreVersion])

    def get_version(
        self, *, app_id: str, version_string: str
    ) -> AppStoreVersion | None:
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
    ) -> AppStoreVersionPhasedRelease | None:
        """Get the phased release of given app version

        :param version_id: The version ID to query for phased releases

        :returns: An AppStoreVersionPhasedRelease if found, None otherwise
        """
        self.log.debug(f"Getting phased release of {version_id}")
        url = self.http_client.generate_url(
            f"appStoreVersions/{version_id}/appStoreVersionPhasedRelease"
        )

        return next_or_none(
            self.http_client.get(url=url, data_type=AppStoreVersionPhasedRelease)
        )

    def create_phased_release(
        self,
        *,
        version_id: str,
        phased_release_state: PhasedReleaseState = PhasedReleaseState.INACTIVE,
    ) -> AppStoreVersionPhasedRelease | None:
        """Create a phased release for a given app version, defaulting to creating an inactive release.

        :param version_id: The version ID to query for phased releases
        :param phased_release_state: the state of the initial rollout

        :returns: An AppStoreVersionPhasedRelease if found, None otherwise
        """

        self.log.info(
            f"Creating phased release ({phased_release_state}) for version {version_id}"
        )

        return self.http_client.post(
            endpoint="appStoreVersionPhasedReleases",
            data={
                "data": {
                    "attributes": {"phasedReleaseState": phased_release_state.value},
                    "type": "appStoreVersionPhasedReleases",
                    "relationships": {
                        "appStoreVersion": {
                            "data": {"id": version_id, "type": "appStoreVersions"}
                        }
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
        self.http_client.delete(
            url=f"appStoreVersionPhasedReleases/{phased_release_id}"
        )

    def patch_phased_release(
        self,
        *,
        phased_release_id: str,
        phased_release_state: PhasedReleaseState = PhasedReleaseState.INACTIVE,
    ) -> AppStoreVersionPhasedRelease | None:
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

    def get_localizations(
        self, *, version_id: str
    ) -> Iterator[AppStoreVersionLocalization]:
        """Get the version localizations for an app version.

        :param version_id: The version ID to get the localizations for

        :returns: An AppStoreVersion
        """
        self.log.info(f"Getting localizations for version {version_id}...")
        url = self.http_client.generate_url(
            f"appStoreVersions/{version_id}/appStoreVersionLocalizations"
        )
        yield from self.http_client.get(
            url=url, data_type=list[AppStoreVersionLocalization]
        )

    def get_attached_build(self, *, version_id: str) -> Build | None:
        """Get the build that is attached to a specific App Store version.

        :param version_id: The version ID to get the build for

        :returns: A Build
        """
        self.log.info(f"Getting build for version {version_id}...")

        url = self.http_client.generate_url(f"appStoreVersions/{version_id}/build")

        return next_or_none(self.http_client.get(url=url, data_type=Build))

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

    def get_app_review_details(
        self, *, version_id: str
    ) -> AppStoreReviewDetails | None:
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

    # pylint:disable=too-many-arguments
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
                        "appStoreVersion": {
                            "data": {"type": "appStoreVersions", "id": version_id}
                        }
                    },
                }
            },
            data_type=AppStoreReviewDetails,
        )

    # pylint:enable=too-many-arguments

    def get_idfa(self, *, version_id: str) -> IdfaDeclaration | None:
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
                        "appStoreVersion": {
                            "data": {"type": "appStoreVersions", "id": version_id}
                        }
                    },
                }
            },
            data_type=IdfaDeclaration,
        )

    def set_attribute(
        self,
        *,
        version_id: str,
        attribute_name: str,
        attribute_value: bool | str | int | float | None,
    ) -> AppStoreVersion:
        """Set an attribute on the version.

        :param version_id: The ID of the version to set the build on
        :param attribute_name: The name of the attribute to set
        :param attribute_value: The value of the attribute to set

        :returns: The patched version
        """

        self.log.info(
            f"Setting {attribute_name} to {attribute_value} for version {version_id}"
        )

        return self.http_client.patch(
            endpoint=f"appStoreVersions/{version_id}",
            data={
                "data": {
                    "type": "appStoreVersions",
                    "id": version_id,
                    "attributes": {attribute_name: attribute_value},
                }
            },
            data_type=AppStoreVersion,
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

        return self.set_attribute(
            version_id=version_id, attribute_name="usesIdfa", attribute_value=True
        )

    def set_version_string(
        self,
        *,
        version_id: str,
        version_string: str,
    ) -> AppStoreVersion:
        """Set the version string.

        :param version_id: The ID of the version to set the build on
        :param version_string: The version string to set

        :returns: The patched app
        """

        self.log.info(f"Setting version to {version_string} for version {version_id}")

        return self.set_attribute(
            version_id=version_id,
            attribute_name="versionString",
            attribute_value=version_string,
        )

    def submit_for_review(
        self,
        *,
        app_id: str,
        version_id: str,
        platform: Platform,
        max_attempts: int = 3,
    ) -> ReviewSubmission:
        """Submit an app store version for review.

        Apple's ``reviewSubmissions`` flow requires three sequential calls:
        create the submission, add the version to it as a
        ``reviewSubmissionItem``, then PATCH the submission with
        ``submitted=true``. Creating the submission on its own does *not*
        submit anything - the version stays in ``PREPARE_FOR_SUBMISSION``
        indefinitely.

        Only one non-``COMPLETE`` review submission may exist per app at a
        time, so this reuses an existing draft (``READY_FOR_REVIEW``) when one
        is present, and treats an already-submitted submission as success.
        That also makes the call idempotent across the transient (5xx) retries
        below: a retry re-discovers the partially-created submission - whether
        it already holds the version or still needs it submitted - instead of
        creating a duplicate or re-adding the item.

        This is *not* safe to run concurrently for the same app: two callers can
        both find no open submission and both try to create one. The loser's
        create is handled (it re-discovers and reuses the winner's submission),
        but two callers racing to attach *different* versions is undefined.

        :param app_id: The ID of the app to submit for review
        :param version_id: The ID of the app store version to submit
        :param platform: The platform to submit for review
        :param max_attempts: The number of attempts allowed for transient (5xx) failures

        :returns: The review submission. When this call performs the submit, it
                  is the submission as returned by the submit PATCH (whose body
                  reflects the new pipeline state); when an in-flight submission
                  already existed, it is that submission.
        :raises ValueError: If a reused submission already holds different content
        :raises AppStoreConnectError: If it runs into an unretriable error or exceeds the retry count
        """

        try:
            submission = self._find_or_create_review_submission(
                app_id=app_id, platform=platform
            )

            if submission.attributes.state != ReviewSubmissionState.READY_FOR_REVIEW:
                # The submission has already been submitted and is somewhere in
                # Apple's pipeline (WAITING_FOR_REVIEW / IN_REVIEW /
                # UNRESOLVED_ISSUES / CANCELING / COMPLETING). Treating this as
                # success is only correct when the in-flight submission is the
                # one for *our* version - then the submit already happened and a
                # re-run is a genuine no-op. If a *different* version is in
                # review, returning success here would be a silent lie: Apple
                # allows only one open submission per app, so version_id was
                # never submitted and cannot be until that submission clears.
                # Refuse loudly rather than reporting a submit that did not
                # happen.
                if not self._submission_contains_version(
                    submission_id=submission.identifier, version_id=version_id
                ):
                    raise ValueError(
                        f"App {app_id} already has an in-flight review submission "
                        f"{submission.identifier} (state "
                        f"{submission.attributes.state.value}) that does not "
                        f"contain version {version_id}. Apple allows only one "
                        f"open submission per app, so version {version_id} "
                        f"cannot be submitted until that submission completes or "
                        f"is cancelled."
                    )

                self.log.info(
                    f"App {app_id} already has review submission "
                    f"{submission.identifier} containing version {version_id} in "
                    f"state {submission.attributes.state.value}; nothing to submit"
                )
                return submission

            self._ensure_version_attached(
                submission_id=submission.identifier, version_id=version_id
            )

            # The PATCH response is the authoritative post-submit state (it is
            # read-your-write for this same request), so we trust it rather than
            # issuing a separate GET. A follow-up GET can lag Apple's eventual
            # consistency and momentarily still report READY_FOR_REVIEW, which
            # would wrongly fail a submission that actually went through.
            submitted = self._mark_review_submission_submitted(
                submission_id=submission.identifier
            )

            self.log.info(
                f"Submitted review submission {submitted.identifier} for review "
                f"(state: {submitted.attributes.state.value})"
            )
            return submitted

        except AppStoreConnectError as ex:
            if max_attempts > 0 and 500 <= ex.response.status_code < 600:
                self.log.info(
                    f"Submit failed due to server-side intermittent issue. Will sleep for 1 minute and try again, left attempt: {max_attempts - 1}."
                )
                time.sleep(60)
                return self.submit_for_review(
                    app_id=app_id,
                    version_id=version_id,
                    platform=platform,
                    max_attempts=max_attempts - 1,
                )

            raise  # Re-raise the caught exception

    def _get_open_review_submission(
        self, *, app_id: str, platform: Platform
    ) -> ReviewSubmission | None:
        """Get the current non-complete review submission for an app, if any.

        Apple permits only one review submission per app that is not in the
        ``COMPLETE`` state. This returns it - whether a reusable draft or one
        that has already been submitted - so the caller can reuse it instead of
        conflicting when trying to create a new one.

        :param app_id: The ID of the app
        :param platform: The platform to filter to

        :returns: The open review submission, or None if there isn't one
        """

        url = self.http_client.generate_url("reviewSubmissions")
        url = update_query_parameters(
            url,
            {
                "filter[app]": app_id,
                "filter[platform]": platform.value,
                # Everything except COMPLETE is "open". COMPLETING is included
                # here on purpose (it is excluded only from COMPLETE): an
                # in-flight COMPLETING submission must be discovered so we treat
                # it as already-submitted instead of trying to create a second
                # one and hitting Apple's one-open-submission-per-app rule.
                "filter[state]": ",".join(
                    state.value
                    for state in ReviewSubmissionState
                    if state != ReviewSubmissionState.COMPLETE
                ),
            },
        )

        submissions = list(
            self.http_client.get(url=url, data_type=list[ReviewSubmission])
        )

        if len(submissions) > 1:
            # Apple's invariant is at most one non-COMPLETE submission per app.
            # If that is ever violated, surface it rather than silently picking
            # an arbitrary row - it signals a broken assumption upstream.
            self.log.warning(
                f"Expected at most one open review submission for app {app_id} "
                f"on {platform.value}, found {len(submissions)}: "
                f"{[submission.identifier for submission in submissions]}. "
                f"Using the first."
            )

        return submissions[0] if submissions else None

    def _find_or_create_review_submission(
        self, *, app_id: str, platform: Platform
    ) -> ReviewSubmission:
        """Return the app's open review submission, creating one if needed.

        Reuses the existing non-``COMPLETE`` submission when present (in any
        state). If none exists a new draft is created; should that create race
        a concurrent submitter and lose with a 409, the now-existing submission
        is re-discovered and returned rather than failing.

        :param app_id: The ID of the app
        :param platform: The platform to submit for

        :returns: The open (reused or freshly created) review submission
        :raises AppStoreConnectError: On a non-conflict create failure, or a
                                      conflict that leaves nothing to reuse
        """

        existing = self._get_open_review_submission(app_id=app_id, platform=platform)

        if existing is not None:
            self.log.info(
                f"Reusing existing review submission {existing.identifier} "
                f"(state: {existing.attributes.state.value})"
            )
            return existing

        try:
            return self._create_review_submission(app_id=app_id, platform=platform)
        except AppStoreConnectError as ex:
            # A concurrent submitter can create the single allowed open
            # submission between our lookup and this create, yielding a 409
            # Conflict. Re-discover and reuse it instead of failing the run.
            if ex.response.status_code != 409:
                raise

            self.log.info(
                f"Create conflicted for app {app_id}; re-fetching the existing "
                f"open submission"
            )
            reused = self._get_open_review_submission(app_id=app_id, platform=platform)
            if reused is None:
                raise

            return reused

    def _create_review_submission(
        self, *, app_id: str, platform: Platform
    ) -> ReviewSubmission:
        """Create a new (empty) review submission for an app.

        :param app_id: The ID of the app
        :param platform: The platform to submit for

        :returns: The newly created review submission
        """

        self.log.info(f"Creating review submission for app {app_id}")

        submission = self.http_client.post(
            endpoint="reviewSubmissions",
            data={
                "data": {
                    "type": "reviewSubmissions",
                    "attributes": {"platform": platform.value},
                    "relationships": {"app": {"data": {"type": "apps", "id": app_id}}},
                }
            },
            data_type=ReviewSubmission,
            log_response=True,
        )

        assert submission is not None, "Creating the review submission returned no data"

        return submission

    def _get_review_submission_items(
        self, submission_id: str
    ) -> list[ReviewSubmissionItem]:
        """Get all items currently attached to a review submission.

        ``include=appStoreVersion`` is requested so each item carries the
        ``data`` linkage identifying the version it references (see
        :meth:`_item_version_id`).

        :param submission_id: The ID of the review submission

        :returns: The list of attached items (empty if the submission has none)
        """

        url = self.http_client.generate_url(f"reviewSubmissions/{submission_id}/items")
        url = update_query_parameters(url, {"include": "appStoreVersion"})
        return list(self.http_client.get(url=url, data_type=list[ReviewSubmissionItem]))

    @staticmethod
    def _item_version_id(item: ReviewSubmissionItem) -> str | None:
        """Return the app store version ID a submission item references, if any.

        :param item: The review submission item

        :returns: The app store version ID, or None when the item references a
                  different kind of resource (e.g. an in-app event) or the
                  linkage was not returned
        """

        if item.relationships is None:
            return None

        relationship = item.relationships.get("appStoreVersion")
        if relationship is None or relationship.data is None:
            return None

        return relationship.data.identifier

    def _submission_contains_version(
        self, *, submission_id: str, version_id: str
    ) -> bool:
        """Return whether the submission already holds ``version_id`` as an item.

        Used to tell an idempotent re-run of *this* version's submission (the
        version is present) apart from a different version already occupying the
        app's single allowed open submission (it is not).

        :param submission_id: The ID of the review submission
        :param version_id: The ID of the app store version to look for

        :returns: True if an attached item references ``version_id``
        """

        items = self._get_review_submission_items(submission_id)
        return any(self._item_version_id(item) == version_id for item in items)

    def _ensure_version_attached(self, *, submission_id: str, version_id: str) -> None:
        """Make sure exactly ``version_id`` is attached to the submission.

        A freshly created submission has no items and the version is added. A
        reused draft may already hold the version from an earlier partial run,
        in which case it must not be added again - Apple rejects duplicate
        items. If the draft instead holds *different* content (another version,
        or a non-version item), submitting it would push the wrong thing to App
        Review while leaving ``version_id`` unsubmitted, so this refuses loudly
        rather than silently submitting the wrong submission.

        :param submission_id: The ID of the review submission
        :param version_id: The ID of the app store version that must be attached

        :raises ValueError: If the submission already holds different content
        """

        items = self._get_review_submission_items(submission_id)

        # Only skip the add when *every* existing item is our version (normally
        # just the single item from an earlier partial run). Checking ``all``
        # rather than ``any`` matters: a draft holding our version *and* a
        # foreign one would otherwise short-circuit here and get submitted with
        # the foreign content still attached.
        if items and all(self._item_version_id(item) == version_id for item in items):
            self.log.info(
                f"Review submission {submission_id} already contains only version "
                f"{version_id}; not adding it again"
            )
            return

        if items:
            attached = ", ".join(
                self._item_version_id(item) or item.identifier for item in items
            )
            raise ValueError(
                f"Review submission {submission_id} already contains items "
                f"({attached}) that do not all match version {version_id}; "
                f"refusing to submit it. Resolve or cancel the existing "
                f"submission first."
            )

        self._add_version_to_review_submission(
            submission_id=submission_id, version_id=version_id
        )

    def _add_version_to_review_submission(
        self, *, submission_id: str, version_id: str
    ) -> None:
        """Attach an app store version to a review submission as an item.

        :param submission_id: The ID of the review submission
        :param version_id: The ID of the app store version to attach
        """

        self.log.info(
            f"Adding version {version_id} to review submission {submission_id}"
        )

        self.http_client.post(
            endpoint="reviewSubmissionItems",
            data={
                "data": {
                    "type": "reviewSubmissionItems",
                    "relationships": {
                        "reviewSubmission": {
                            "data": {"type": "reviewSubmissions", "id": submission_id}
                        },
                        "appStoreVersion": {
                            "data": {"type": "appStoreVersions", "id": version_id}
                        },
                    },
                }
            },
            log_response=True,
        )

    def _mark_review_submission_submitted(
        self, *, submission_id: str
    ) -> ReviewSubmission:
        """Submit a prepared review submission by setting ``submitted`` to true.

        This is the call that actually sends the submission to App Review and
        moves the version from ``PREPARE_FOR_SUBMISSION`` to
        ``WAITING_FOR_REVIEW``. The returned submission is the PATCH response
        body, which reflects the post-submit state without a separate (and
        potentially lagging) read.

        :param submission_id: The ID of the review submission to submit

        :returns: The submitted review submission
        """

        self.log.info(f"Marking review submission {submission_id} as submitted")

        submission = self.http_client.patch(
            endpoint=f"reviewSubmissions/{submission_id}",
            data={
                "data": {
                    "type": "reviewSubmissions",
                    "id": submission_id,
                    "attributes": {"submitted": True},
                }
            },
            data_type=ReviewSubmission,
            log_response=True,
        )

        assert (
            submission is not None
        ), "Submitting the review submission returned no data"

        return submission

    def release(
        self,
        *,
        version_id: str,
        max_attempts: int = 3,
    ) -> None:
        """Release an approved version

        :param version_id: The ID of the version to release
        :param max_attempts: The number of attempts allowed

        :raises AppStoreConnectError: If runs into unretriable error or exceeds retry count
        """

        try:
            self.log.info(f"Releasing version {version_id}")

            self.http_client.post(
                endpoint="appStoreVersionReleaseRequests",
                data={
                    "data": {
                        "type": "appStoreVersionReleaseRequests",
                        "relationships": {
                            "appStoreVersion": {
                                "data": {"type": "appStoreVersions", "id": version_id}
                            }
                        },
                    }
                },
                log_response=True,
            )

        except AppStoreConnectError as ex:
            if (
                max_attempts > 0
                and ex.response.status_code >= 500
                and ex.response.status_code < 600
            ):
                self.log.info(
                    f"Submit failed due to server-side intermittent issue. Will sleep for 1 minute and try again, left attempt: {max_attempts - 1}."
                )
                time.sleep(60)
                self.release(version_id=version_id, max_attempts=max_attempts - 1)
            else:
                raise  # Re-raise the caught exception
