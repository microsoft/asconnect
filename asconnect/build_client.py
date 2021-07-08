"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
import os
import time
from typing import Iterator, List, Optional

from asconnect.httpclient import HttpClient

from asconnect.altool import upload, Platform
from asconnect.models import App, Build, BuildBetaDetail
from asconnect.sorting import BuildsSort
from asconnect.utilities import update_query_parameters, next_or_none, write_key


class BuildClient:
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
        self.log = log.getChild("build")

    def get_builds(
        self,
        *,
        url: Optional[str] = None,
        sort: Optional[BuildsSort] = None,
        build_number: Optional[str] = None,
        version: Optional[str] = None,
        app_id: Optional[str] = None,
    ) -> Iterator[Build]:
        """Get all builds.

        :param Optional[str] url: The URL to use (will be generated if not supplied)
        :param Optional[BuildSort] sort: The sort option to use
        :param Optional[str] build_number: Filter to just this build number
        :param Optional[str] version: Filter to just this version
        :param Optional[str] app_id: Filter to just this app

        :returns: A list of builds
        """

        self.log.info("Getting builds...")

        if url is None:
            url = self.http_client.generate_url("builds")

        query_parameters = {}

        if sort:
            query_parameters["sort"] = sort.value

        if build_number:
            query_parameters["filter[version]"] = build_number

        if app_id:
            query_parameters["filter[app]"] = app_id

        if version:
            query_parameters["filter[preReleaseVersion.version]"] = version

        url = update_query_parameters(url, query_parameters)

        yield from self.http_client.get(url=url, data_type=List[Build])

    def get_build_from_identifier(self, identifier: str) -> Optional[Build]:
        """Get a build from its identifier

        :param identifier: The unique identifier for the build (_not_ the build number)

        :returns: A build if found, None otherwise
        """

        self.log.info(f"Getting build {identifier}")

        url = self.http_client.generate_url(f"builds/{identifier}")

        return next_or_none(self.http_client.get(url=url, data_type=Build))

    def get_from_build_number(self, bundle_id: str, build_number: str) -> Optional[Build]:
        """Get a build from its build number.

        :param bundle_id: The bundle ID of the app
        :param build_number: The build number for the build to get

        :returns: The build if found, None otherwise
        """

        self.log.info(f"Getting build from build number {build_number} for bundle {bundle_id}")

        for build in self.get_builds(build_number=build_number):
            self.log.debug(f"Checking build {build}")

            # TODO use app id directly for this
            assert build.relationships is not None
            related_link = build.relationships["app"].links.related
            assert related_link is not None
            app = next_or_none(self.http_client.get(url=related_link, data_type=App))

            if not app:
                break

            if app.bundle_id == bundle_id:
                return build

        return None

    def wait_for_build_to_process(
        self, bundle_id: str, build_number: str, wait_time: int = 30
    ) -> Build:
        """Wait for a build to finish processing.

        :param bundle_id: The ID of the app
        :param build_number: The build number for the build to wait for
        :param wait_time: The time to wait between checks for processing completion in seconds

        :returns: The build when finished processing
        """
        build = None

        while True:
            self.log.info("Waiting for build to appear...")
            build = self.get_from_build_number(bundle_id, build_number)
            if build is not None:
                break
            time.sleep(wait_time)

        if build.attributes.processing_state != "PROCESSING":
            return build

        while True:
            build = self.get_build_from_identifier(build.identifier)
            assert build is not None

            if build.attributes.processing_state != "PROCESSING":
                return build

            self.log.info(
                f"Build {build_number} has not finished processing. Will check again in {wait_time} seconds..."
            )
            time.sleep(wait_time)

    def get_beta_detail(self, build: Build) -> Optional[BuildBetaDetail]:
        """Get the build beta details.

        :param build: The build to get the beta details for

        :returns: An iterator to the beta app localizations
        """
        self.log.debug(f"Get beta detail for build {build}")
        assert build.relationships is not None
        url = build.relationships["buildBetaDetail"].links.related
        return next_or_none(self.http_client.get(url=url, data_type=BuildBetaDetail))

    def upload(self, ipa_path: str, platform: Platform) -> None:
        """Upload a build to App Store Connect.

        :param ipa_path: The path to the IPA
        :param platform: The platform the app is for
        """

        self.log.info(f"Uploading IPA {ipa_path} for platform {platform}")

        key_path = write_key(self.http_client.key_id, self.http_client.key_contents)

        try:
            upload(
                ipa_path=ipa_path,
                platform=platform,
                key_id=self.http_client.key_id,
                issuer_id=self.http_client.issuer_id,
                log=self.log,
            )

        finally:
            os.remove(key_path)
