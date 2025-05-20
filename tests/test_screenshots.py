# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Tests for the package."""

import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import asconnect  # pylint: disable=wrong-import-order


# pylint: disable=too-many-lines


def test_get_screenshot_sets(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get screenshot sets from app store version."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    localizations = list(client.version.get_localizations(version_id=version.identifier))
    assert len(localizations) > 0

    en_us = [
        localization for localization in localizations if localization.attributes.locale == "en-US"
    ][0]

    screenshot_sets = list(client.screenshots.get_sets(localization_id=en_us.identifier))
    assert len(screenshot_sets) > 0


def test_get_screenshots(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get screenshot sets from app store version."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    localizations = list(client.version.get_localizations(version_id=version.identifier))
    assert len(localizations) > 0

    en_us = [
        localization for localization in localizations if localization.attributes.locale == "en-US"
    ][0]

    screenshot_set = list(client.screenshots.get_sets(localization_id=en_us.identifier))[0]

    screenshots = list(
        client.screenshots.get_screenshots(screenshot_set_id=screenshot_set.identifier)
    )
    assert len(screenshots) > 0


def test_delete_screenshot_sets(client: asconnect.Client, app_id: str) -> None:
    """Test that we can delete screenshot sets from app store version."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    for localization in client.version.get_localizations(version_id=version.identifier):
        client.screenshots.delete_all_sets_in_localization(localization_id=localization.identifier)

    assert version is not None


def test_create_screenshot_set(client: asconnect.Client, app_id: str) -> None:
    """Test that we can create a screenshot set."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    localizations = list(client.version.get_localizations(version_id=version.identifier))

    en_us = [
        localization for localization in localizations if localization.attributes.locale == "en-US"
    ][0]

    client.screenshots.create_set(
        localization_id=en_us.identifier,
        display_type=asconnect.models.ScreenshotDisplayType.APP_IPHONE_65,
    )


def test_create_screenshot(client: asconnect.Client, app_id: str) -> None:
    """Test that we can create a screenshot set."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    localizations = list(client.version.get_localizations(version_id=version.identifier))

    en_us = [
        localization for localization in localizations if localization.attributes.locale == "en-US"
    ][0]

    client.screenshots.delete_all_sets_in_localization(localization_id=en_us.identifier)

    screenshot_set = client.screenshots.create_set(
        localization_id=en_us.identifier,
        display_type=asconnect.models.ScreenshotDisplayType.APP_IPHONE_65,
    )

    screenshot = client.screenshots.upload_screenshot(
        file_path="/path/to/screenshot.png",
        screenshot_set_id=screenshot_set.identifier,
    )

    print(screenshot)


class ScreenshotFile:
    """Represents a screenshot file."""

    filename: str
    path: str
    root_path: str
    prefix: str
    order_key: int
    description: str
    md5: str

    _PATTERN = re.compile(r"([^-]*)-0*([0-9]*)-?(.*)\.png")

    def __init__(self, filename: str, root_path: str) -> None:
        """Create a new instance.

        :param filename: The name of the file
        :param root_path: The path the file lives under
        """
        match = ScreenshotFile._PATTERN.match(filename)
        assert match
        self.filename = filename
        self.path = os.path.join(root_path, filename)
        self.root_path = root_path
        self.prefix = match.group(1)
        self.order = int(match.group(2))
        self.description = match.group(3) if match.group(3) else ""
        self.md5 = asconnect.utilities.md5_file(os.path.join(root_path, filename))


# pylint: disable=too-many-locals
def upload_screenshots_for_localization(
    localization: asconnect.models.AppStoreVersionLocalization,
    root_screenshots_path: str,
    client: asconnect.Client,
) -> None:
    """Upload the screenshots for a localization

    :param localization: The localization to upload the screenshots for
    :param root_screenshots_path: The root path the screenshots live at
    :param client: The API client

    :raises FileNotFoundError: If the screenshots path doesn't exist
    """
    screenshots_path = os.path.join(root_screenshots_path, localization.attributes.locale)

    if not os.path.exists(screenshots_path):
        raise FileNotFoundError(
            f"Could not find screenshots for locale {localization.attributes.locale} in {root_screenshots_path}"
        )

    screenshot_files = [
        ScreenshotFile(file_name, screenshots_path)
        for file_name in os.listdir(screenshots_path)
        if file_name.endswith(".png")
    ]

    prefixes = {file_name.prefix for file_name in screenshot_files}

    existing_sets = {
        screenshot_set.attributes.screenshot_display_type: screenshot_set
        for screenshot_set in client.screenshots.get_sets(localization_id=localization.identifier)
    }

    handled_displays = set()

    uploads = []

    for prefix in prefixes:
        display_type = asconnect.models.ScreenshotDisplayType.from_name(prefix)

        if display_type is None:
            # self.log.warning(f"Could not get display type for: {prefix}")
            continue

        handled_displays.add(display_type)

        screenshots = [screenshot for screenshot in screenshot_files if screenshot.prefix == prefix]
        screenshots.sort(key=lambda screenshot: screenshot.order)

        existing_set = existing_sets.get(display_type)

        # If we have an existing one, check if the images are the same. If not, wipe it and re-upload
        if existing_set is not None:
            existing_screenshots = client.screenshots.get_screenshots(
                screenshot_set_id=existing_set.identifier
            )

            checksums = {screenshot.md5 for screenshot in screenshots}
            for existing_screenshot in existing_screenshots:
                if (
                    existing_screenshot.attributes.source_file_checksum is None
                    or existing_screenshot.attributes.source_file_checksum not in checksums
                ):
                    client.screenshots.delete_set(
                        screenshot_set_id=existing_set.identifier, delete_all_screenshots=True
                    )
                    break
            else:
                # All images were the same so continue
                continue

        uploads.append((localization.identifier, display_type, screenshots))

    unhandled_displays = set(existing_sets.keys()) - handled_displays

    for unhandled_display in unhandled_displays:
        existing_set = existing_sets.get(unhandled_display)
        if existing_set is None:
            continue
        client.screenshots.delete_set(
            screenshot_set_id=existing_set.identifier, delete_all_screenshots=True
        )

    for localization_id, display_type, screenshots in uploads:
        screenshot_set = client.screenshots.create_set(
            localization_id=localization_id, display_type=display_type
        )

        for screenshot in screenshots:
            client.screenshots.upload_screenshot(
                file_path=screenshot.path, screenshot_set_id=screenshot_set.identifier
            )


# pylint: enable=too-many-locals


def test_upload_all_screenshots(client: asconnect.Client, app_id: str) -> None:
    """Test that we can upload all screenshots."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    root_screenshots_path = "/path/to/screenshots"

    for localization in client.version.get_localizations(version_id=version.identifier):
        upload_screenshots_for_localization(localization, root_screenshots_path, client)

    print("Done")
