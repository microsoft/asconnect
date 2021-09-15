"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
import os
from typing import Iterator, List

from asconnect.exceptions import AppStoreConnectError
from asconnect.httpclient import HttpClient
from asconnect.models import AppScreenshotSet, AppScreenshot, ScreenshotDisplayType, UploadOperation
from asconnect.utilities import md5_file


class ScreenshotClient:
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
        self.log = log.getChild("screenshot")

    def get_sets(
        self,
        *,
        localization_id: str,
    ) -> Iterator[AppScreenshotSet]:
        """Get the screenshot sets for an app localization.

        :param localization_id: The localization ID to get the screenshot sets for

        :returns: An iterator to ScreenshotSet
        """
        self.log.debug(f"Getting screenshot sets for {localization_id}...")
        url = self.http_client.generate_url(
            f"appStoreVersionLocalizations/{localization_id}/appScreenshotSets"
        )
        yield from self.http_client.get(url=url, data_type=List[AppScreenshotSet])

    def delete_set(self, *, screenshot_set_id: str, delete_all_screenshots: bool = True) -> None:
        """Delete a screenshot set.

        :param screenshot_set_id: The ID of the screenshot set to delete
        :param delete_all_screenshots: If this is True, any screenshots will be deleted first.

        :raises AppStoreConnectError: On failure to delete
        """

        self.log.info(f"Deleting screenshot set {screenshot_set_id}")

        if delete_all_screenshots:
            self.delete_screenshots_in_set(screenshot_set_id=screenshot_set_id)

        url = self.http_client.generate_url(f"appScreenshotSets/{screenshot_set_id}")
        raw_response = self.http_client.delete(url=url)

        if raw_response.status_code != 204:
            raise AppStoreConnectError(raw_response)

    def get_screenshots(
        self,
        *,
        screenshot_set_id: str,
    ) -> Iterator[AppScreenshot]:
        """Get the screenshots for a set.

        :param screenshot_set_id: The screenshot set ID to get the screenshots for

        :returns: An iterator to AppScreenshot
        """
        self.log.debug(f"Getting screenshots {screenshot_set_id}")
        url = self.http_client.generate_url(f"appScreenshotSets/{screenshot_set_id}/appScreenshots")
        yield from self.http_client.get(url=url, data_type=List[AppScreenshot])

    def delete_screenshot(self, *, screenshot_id: str) -> None:
        """Delete a screenshot.

        :param screenshot_id: The ID of the screenshot to delete

        :raises AppStoreConnectError: On failure to delete
        """
        self.log.info(f"Deleting screenshot {screenshot_id}")
        url = self.http_client.generate_url(f"appScreenshots/{screenshot_id}")
        raw_response = self.http_client.delete(url=url)

        if raw_response.status_code != 204:
            raise AppStoreConnectError(raw_response)

    def delete_screenshots_in_set(self, *, screenshot_set_id: str) -> None:
        """Delete all screenshots in set.

        :param screenshot_set_id: The set to delete the screenshots in
        """
        self.log.info(f"Deleting screenshots in set {screenshot_set_id}")
        for screenshot in self.get_screenshots(screenshot_set_id=screenshot_set_id):
            self.log.info(f"Deleting screenshot {screenshot.attributes.file_name}")
            self.delete_screenshot(screenshot_id=screenshot.identifier)

    def delete_all_sets_in_localization(self, *, localization_id: str) -> None:
        """Delete all the sets in a localization.

        :param localization_id: The localization to delete the sets from
        """
        self.log.info(f"Deleting all screenshot sets in localization {localization_id}")
        for screenshot_set in self.get_sets(localization_id=localization_id):
            self.log.info(
                f"Deleting screenshot set: {screenshot_set.attributes.screenshot_display_type.value}"
            )
            self.delete_set(
                screenshot_set_id=screenshot_set.identifier, delete_all_screenshots=True
            )

    def create_set(
        self, *, localization_id: str, display_type: ScreenshotDisplayType
    ) -> AppScreenshotSet:
        """Create a screenshot set for an app localization.

        :param localization_id: The localization ID to create the screenshot set for
        :param display_type: The type of preview that the set is for

        :raises AppStoreConnectError: On error when creating the set

        :returns: The new screenshot set
        """

        self.log.info(f"Creating screenshot set {localization_id} / {display_type}")

        data = {
            "data": {
                "attributes": {"screenshotDisplayType": display_type.value},
                "type": "appScreenshotSets",
                "relationships": {
                    "appStoreVersionLocalization": {
                        "data": {
                            "type": "appStoreVersionLocalizations",
                            "id": localization_id,
                        }
                    }
                },
            }
        }

        self.log.debug(f"Data: {data}")

        return self.http_client.post(
            endpoint="appScreenshotSets",
            data=data,
            data_type=AppScreenshotSet,
        )

    def _create_screenshot_reservation(
        self, *, file_path: str, screenshot_set_id: str
    ) -> AppScreenshot:
        """Create a screenshot reservation

        :param file_path: The path to the screenshot to reserve
        :param screenshot_set_id: The id for the screenshot set to reserve in

        :raises AppStoreConnectError: On error when creating the set

        :returns: The new screenshot set
        """

        self.log.debug(f"Creating screenshot reservarion for {screenshot_set_id} at {file_path}")

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        return self.http_client.post(
            endpoint="appScreenshots",
            data={
                "data": {
                    "attributes": {"fileName": file_name, "fileSize": file_size},
                    "type": "appScreenshots",
                    "relationships": {
                        "appScreenshotSet": {
                            "data": {
                                "type": "appScreenshotSets",
                                "id": screenshot_set_id,
                            }
                        }
                    },
                }
            },
            data_type=AppScreenshot,
        )

    def _upload_screenshot_contents(
        self, *, file_path: str, upload_operations: List[UploadOperation]
    ) -> None:
        """Upload a screenshots contents

        :param file_path: The path to the screenshot to upload
        :param upload_operations: The upload operations for the screenshot

        :raises AppStoreConnectError: On error when creating the set
        """

        self.log.debug(f"Uploading screenshot contents {file_path}: {upload_operations}")

        # Start by ordering the upload oeprations by offset (so we can just go in order)
        upload_operations = sorted(upload_operations, key=lambda operation: operation.offset)

        with open(file_path, "rb") as screenshot:
            for operation in upload_operations:
                data = screenshot.read(operation.length)
                headers = {header.name: header.value for header in operation.request_headers}
                raw_response = self.http_client.put_chunk(
                    url=operation.url, additional_headers=headers, data=data
                )
                # TODO Check this
                assert raw_response.ok

    def _set_screenshot_uploaded(
        self, *, screenshot: AppScreenshot, file_hash: str
    ) -> AppScreenshot:
        """Marks a screenshot as uploaded

        :param screenshot: The screenshot to mark as uploaded
        :param file_hash: The MD5 of the file

        :returns: The new screenshot
        """

        self.log.debug(f"Setting screenshot uploaded {screenshot}: {file_hash}")

        return self.http_client.patch(
            endpoint=f"appScreenshots/{screenshot.identifier}",
            data={
                "data": {
                    "attributes": {"uploaded": True, "sourceFileChecksum": file_hash},
                    "type": "appScreenshots",
                    "id": screenshot.identifier,
                }
            },
            data_type=AppScreenshot,
        )

    def upload_screenshot(self, *, file_path: str, screenshot_set_id: str) -> AppScreenshot:
        """Upload a screenshot

        :param file_path: The path to the screenshot to upload
        :param screenshot_set_id: The id for the screenshot set to upload to

        :return: The screenshot
        """

        self.log.info(f"Uploading screenshot {file_path} to set {screenshot_set_id}")

        checksum = md5_file(file_path)

        screenshot = self._create_screenshot_reservation(
            file_path=file_path, screenshot_set_id=screenshot_set_id
        )

        assert screenshot.attributes.upload_operations is not None

        self._upload_screenshot_contents(
            file_path=file_path, upload_operations=screenshot.attributes.upload_operations
        )

        return self._set_screenshot_uploaded(screenshot=screenshot, file_hash=checksum)
