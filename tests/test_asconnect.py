# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Tests for the package."""

import datetime
import json
import os
import re
import sys
from typing import Optional, Tuple, Union

import jwt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import asconnect  # pylint: disable=wrong-import-order


# pylint: disable=too-many-lines


APP_ID = ""
IPA_PATH = ""


def get_test_data() -> Tuple[str, str, str]:
    """Get the test data.

    :returns: The test data
    """
    tests_path = os.path.dirname(os.path.abspath(__file__))
    test_data_path = os.path.join(tests_path, "test_data.json")
    with open(test_data_path, "r", encoding="utf-8") as test_data_file:
        all_test_data = json.load(test_data_file)

    test_data = all_test_data["base"]

    return test_data["key_id"], test_data["key"], test_data["issuer_id"]


def test_import() -> None:
    """Test that importing the package works."""
    assert asconnect is not None


def test_token() -> None:
    """Test the JWT token generation"""

    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    token = client.http_client.generate_token()

    decoded = jwt.decode(token, verify=False)
    assert decoded["iss"] == issuer_id
    assert decoded["aud"] == "appstoreconnect-v1"
    assert datetime.datetime.fromtimestamp(
        decoded["exp"]
    ) < datetime.datetime.now() + datetime.timedelta(minutes=20)

    # Ensure we return the cached version
    token2 = client.http_client.generate_token()
    assert token == token2


def test_get_apps() -> None:
    """Test get apps."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )
    apps = list(client.app.get_all())
    assert len(apps) != 0
    print(apps[0])


def test_get_builds() -> None:
    """Test get apps."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )
    builds = client.build.get_builds()
    assert builds is not None


def test_get_builds_by_version() -> None:
    """Test get build by version."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )
    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None
    builds = next(client.build.get_builds(app_id=app.identifier))
    assert builds is not None


def test_get_app() -> None:
    """Test that we can get an app."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )
    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None


def test_upload() -> None:
    """Test that we can upload a build."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    client.build.upload(
        ipa_path=IPA_PATH,
        platform=asconnect.Platform.IOS,
    )


def test_wait_for_build() -> None:
    """Test that we can wait for a build."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )
    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None

    client.build.wait_for_build_to_process(APP_ID, "")


def test_set_testflight_review_details() -> None:
    """Test that we can set the testflight app review details."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )
    app = client.app.get_from_bundle_id(APP_ID)

    assert app is not None

    client.beta_review.set_beta_app_review_details(
        app_id=app.identifier,
        contact_email="j.doe@example.com",
        contact_first_name="John",
        contact_last_name="Doe",
        contact_phone="1-425-867-5309",
        demo_account_name="demo@example.com",
        demo_account_password="P@ssW0rd",
        demo_account_required=True,
    )


def test_get_beta_app_localizations() -> None:
    """Test get beta app localizations."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)

    assert app is not None

    client.beta_review.get_beta_app_localizations(app.identifier)


def test_set_testflight_localized_review_details() -> None:
    """Test that we can set the testflight app review details."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )
    app = client.app.get_from_bundle_id(APP_ID)

    assert app is not None

    info = {
        "en-US": {
            "feedbackEmail": "j.doe@example.com",
            "description": "Thanks for helping us test!",
        }
    }

    client.beta_review.set_beta_app_localizations(app.identifier, info)


def test_get_build_localization_details() -> None:
    """Test that we can get a builds localization details."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    build = client.build.get_from_build_number(build_number="", bundle_id=APP_ID)

    assert build is not None

    assert len(list(client.beta_review.get_beta_build_localizations(build.identifier))) > 0


def test_set_whats_new() -> None:
    """Test that we can get a builds localization details."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    build = client.build.get_from_build_number(build_number="", bundle_id=APP_ID)

    assert build is not None

    client.beta_review.set_whats_new_for_build(
        build.identifier,
        {"en-US": "Bug fixes and performance improvements"},
    )


def test_get_build_beta_detail() -> None:
    """Test that we can get a builds beta details."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    build = client.build.get_from_build_number(build_number="", bundle_id=APP_ID)

    assert build is not None

    build_detail = client.build.get_beta_detail(build)

    assert build_detail is not None


def test_get_beta_groups_detail() -> None:
    """Test that we can get a builds beta details."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)

    assert app is not None

    groups = [
        group
        for group in client.beta_review.get_beta_groups(app.identifier)
        if group.attributes.name in ["External Testers", "Public Link Testers"]
    ]

    assert len(groups) == 2


def test_set_beta_groups_detail() -> None:
    """Test that we can get a builds beta details."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)

    assert app is not None

    build = client.build.get_from_build_number(build_number="", bundle_id=APP_ID)

    assert build is not None

    groups = [
        group
        for group in client.beta_review.get_beta_groups(app.identifier)
        if group.attributes.name in ["External Testers", "Public Link Testers"]
    ]

    client.beta_review.set_beta_groups_on_build(build.identifier, groups)


def test_beta_review_submission() -> None:
    """Test that we can submit a build for beta review."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    build = client.build.get_from_build_number(build_number="", bundle_id=APP_ID)

    assert build is not None

    client.beta_review.submit_for_beta_review(build.identifier)


def test_create_new_version() -> None:
    """Test that we can create a new app store version."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None

    client.app.create_new_version(version="1.2.3", app_id=app.identifier)


def test_create_new_phased_release() -> None:
    """Test that we can create a new app store version."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None

    version = client.app.create_new_version(version="1.2.3", app_id=app.identifier)
    release = client.version.create_phased_release(version_id=version.identifier)

    assert release is not None
    assert release.attributes.phased_release_state is asconnect.models.PhasedReleaseState.INACTIVE


def test_get_versions() -> None:
    """Test that we can get app store versions."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None

    versions = list(client.version.get_all(app_id=app.identifier))
    assert len(versions) > 0


def test_get_version() -> None:
    """Test that we can get a specific app store version."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None


def test_get_version_localizations() -> None:
    """Test that we can get a specific app store version."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    localizations = list(client.version.get_localizations(version_id=version.identifier))
    assert len(localizations) > 0


def test_get_screenshot_sets() -> None:
    """Test that we can get screenshot sets from app store version."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
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


def test_get_screenshots() -> None:
    """Test that we can get screenshot sets from app store version."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
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


def test_delete_screenshot_sets() -> None:
    """Test that we can delete screenshot sets from app store version."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    for localization in client.version.get_localizations(version_id=version.identifier):
        client.screenshots.delete_all_sets_in_localization(localization_id=localization.identifier)

    assert version is not None


def test_create_screenshot_set() -> None:
    """Test that we can create a screenshot set."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
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


def test_create_screenshot() -> None:
    """Test that we can create a screenshot set."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
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


def test_upload_all_screenshots() -> None:
    """Test that we can upload all screenshots."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    root_screenshots_path = "/path/to/screenshots"

    for localization in client.version.get_localizations(version_id=version.identifier):
        upload_screenshots_for_localization(localization, root_screenshots_path, client)

    print("Done")


def test_get_app_info_localization() -> None:
    """Test that we can get app info localization."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id(APP_ID)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    app_infos = client.app_info.get_app_info(app_id=app.identifier)
    app_info = [
        app_info
        for app_info in app_infos
        if app_info.attributes.app_store_state
        != asconnect.models.AppStoreVersionState.READY_FOR_SALE
    ][0]


def test_set_idfa() -> None:
    """Set the advertising ID declaration"""

    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    app = client.app.get_from_bundle_id("com.microsoft.Office.Outlook")
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="4.2135.0")
    assert version is not None

    client.version.set_uses_idfa(version_id=version.identifier)

    _ = client.version.get_idfa(version_id=version.identifier)

    client.version.set_idfa(
        version_id=version.identifier,
        attributes_action_with_previous_ad=True,
        attributes_app_installation_to_previous_ad=True,
        honors_limited_ad_tracking=True,
        serves_ads=True,
    )


def test_get_versions_phased_release() -> None:
    """Test that we can get a specific app store version."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )
    app = client.app.get_from_bundle_id(APP_ID)

    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")

    assert version is not None

    release = client.version.get_phased_release(version_id=version.identifier)

    assert release is not None
    assert release.attributes.phased_release_state is not None


def load_value(
    *,
    root_path: str,
    file_name: str,
    localized_info: Union[
        asconnect.models.AppInfoLocalization, asconnect.models.AppStoreVersionLocalization
    ],
    current_value: Optional[str],
    version: Optional[str] = None,
) -> Optional[str]:
    """Load an app value from the metadata files.

    This checks for values in the following order:

    1. Release specific, language specific
    2. Release specific, language default
    3. Release default, language specific
    4. Release default, language default

    If the determined value matches the current value then None will be returned
    in order to avoid an uneccesary patch call.

    The structure should be something like:
    - root
      - appstore
        - metadata
          - en-US
        - screenshots
          - en-US
      - releases
        - 1.2.3
          - appstore
            - metadata
              - en-US
            - screenshots
              - en-US
          - testflight
            - metadata
              - en-US

    :param root_path: The root path of the repo
    :param file_name: The name of the file to load the value from
    :param localized_info: The localized info this will be going into
    :param current_value: The current value on the app store
    :param version: The version of the app

    :returns: The most specific possible value
    """

    language_code = localized_info.attributes.locale
    assert language_code is not None
    paths_to_check = []

    if version:
        release_metadata_path = os.path.join(root_path, "releases", version, "appstore", "metadata")
        paths_to_check += [
            os.path.join(release_metadata_path, language_code, file_name),
            os.path.join(release_metadata_path, "default", file_name),
        ]

    general_metadata_path = os.path.join(root_path, "appstore", "metadata")

    paths_to_check += [
        os.path.join(general_metadata_path, language_code, file_name),
        os.path.join(general_metadata_path, "default", file_name),
    ]

    for path in paths_to_check:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as metadata_file:
                value = metadata_file.read().strip()

            if value:
                if value == current_value:
                    return None
                return value

    return None


def update_localized_info(
    client: asconnect.Client, localized_info: asconnect.models.AppInfoLocalization
) -> asconnect.models.AppInfoLocalization:
    """Update the localized info on the app store with the latest from disk.

    This uses the same structure as Fastlane to make migration easier

    :param client: The API client
    :param localized_info: The localized info to update

    :returns: The updated localized info
    """
    root_path = "/path/to/metadata"

    name = load_value(
        root_path=root_path,
        file_name="name.txt",
        localized_info=localized_info,
        current_value=localized_info.attributes.name,
    )

    privacy_text = load_value(
        root_path=root_path,
        file_name="privacy_text.txt",
        localized_info=localized_info,
        current_value=localized_info.attributes.privacy_policy_text,
    )

    privacy_url = load_value(
        root_path=root_path,
        file_name="privacy_url.txt",
        localized_info=localized_info,
        current_value=localized_info.attributes.privacy_policy_url,
    )

    subtitle = load_value(
        root_path=root_path,
        file_name="subtitle.txt",
        localized_info=localized_info,
        current_value=localized_info.attributes.subtitle,
    )

    return client.app_info.set_localization_properties(
        localization_id=localized_info.identifier,
        name=name,
        privacy_policy_text=privacy_text,
        privacy_policy_url=privacy_url,
        subtitle=subtitle,
    )


def set_localized_app_info(client: asconnect.Client, app_id: str) -> None:
    """Set the localized info for the app.

    :param client: The API client
    :param app_id: The ID of the app to update the info for
    """

    app_infos = client.app_info.get_app_info(app_id=app_id)
    app_info = [
        app_info
        for app_info in app_infos
        if app_info.attributes.app_store_state
        != asconnect.models.AppStoreVersionState.READY_FOR_SALE
    ][0]

    for localized_info in client.app_info.get_localizations(app_info_id=app_info.identifier):
        update_localized_info(client, localized_info)


def update_localized_version_info(
    client: asconnect.Client,
    localized_info: asconnect.models.AppStoreVersionLocalization,
    version: str,
) -> asconnect.models.AppInfoLocalization:
    """Update the localized info for this version of the app.

    :param client: The API client
    :param localized_info: The localized info to be updated
    :param version: The current version of the app

    :returns: The updated app localization info
    """
    root_path = "/path/to/metadata"

    description = load_value(
        root_path=root_path,
        file_name="description.txt",
        localized_info=localized_info,
        current_value=localized_info.attributes.description,
        version=version,
    )

    keywords = load_value(
        root_path=root_path,
        file_name="keywords.txt",
        localized_info=localized_info,
        current_value=localized_info.attributes.keywords,
        version=version,
    )

    marketing_url = load_value(
        root_path=root_path,
        file_name="marketing_url.txt",
        localized_info=localized_info,
        current_value=localized_info.attributes.marketing_url,
        version=version,
    )

    promotional_text = load_value(
        root_path=root_path,
        file_name="promotional_text.txt",
        localized_info=localized_info,
        current_value=localized_info.attributes.promotional_text,
        version=version,
    )

    support_url = load_value(
        root_path=root_path,
        file_name="support_url.txt",
        localized_info=localized_info,
        current_value=localized_info.attributes.support_url,
    )

    whats_new = load_value(
        root_path=root_path,
        file_name="release_notes.txt",
        localized_info=localized_info,
        current_value=localized_info.attributes.whats_new,
        version=version,
    )

    return client.app_info.set_localization_version_properties(
        version_localization_id=localized_info.identifier,
        description=description,
        keywords=keywords,
        marketing_url=marketing_url,
        promotional_text=promotional_text,
        support_url=support_url,
        whats_new=whats_new,
    )


def set_localized_version_info(client: asconnect.Client, version_id: str, version: str) -> None:
    """Set the localized version info

    :param client: The API client
    :param version_id: The ID of the version to set the info on
    :param version: The current version of the app
    """

    for localized_info in client.version.get_localizations(version_id=version_id):
        update_localized_version_info(client, localized_info, version)

    print("Done")


def set_build(client: asconnect.Client, app_id: str, version_id: str, version: str) -> None:
    """Set the build to the latest

    :param client: The API client
    :param app_id: The app to set the build on
    :param version_id: The ID of the version to set the build on
    :param version: The current version of the app
    """

    build = asconnect.utilities.next_or_none(
        client.build.get_builds(
            app_id=app_id, sort=asconnect.sorting.BuildsSort.UPLOADED_DATE_REVERSED, version=version
        )
    )

    assert build is not None

    client.version.set_build(version_id=version_id, build_id=build.identifier)


def set_app_review_details(client: asconnect.Client, version_id: str) -> None:
    """Set the app review details for the version.

    :param client: The API client
    :param version_id: The version of the app to set the app review details for
    """
    contact_email = "j.doe@example.com"
    contact_first_name = "John"
    contact_last_name = "Doe"
    contact_phone = "1-425-867-5309"
    demo_account_name = "demo@example.com"
    demo_account_password = "P@ssW0rd"
    demo_account_required = True
    notes = ""
    client.version.set_app_review_details(
        version_id=version_id,
        contact_email=contact_email,
        contact_first_name=contact_first_name,
        contact_last_name=contact_last_name,
        contact_phone=contact_phone,
        demo_account_name=demo_account_name,
        demo_account_password=demo_account_password,
        demo_account_required=demo_account_required,
        notes=notes,
    )


def set_idfa(client: asconnect.Client, version_id: str) -> None:
    """Set the advertising ID declaration

    :param client: The API client
    :param version_id: The version of the app to set the advertising ID declaration for
    """
    client.version.set_idfa(
        version_id=version_id,
        attributes_action_with_previous_ad=True,
        attributes_app_installation_to_previous_ad=True,
        honors_limited_ad_tracking=True,
        serves_ads=False,
    )


def test_get_users() -> None:
    """Test that we can upload all screenshots."""
    key_id, key_contents, issuer_id = get_test_data()

    client = asconnect.Client(
        key_id=key_id,
        key_contents=key_contents,
        issuer_id=issuer_id,
    )

    users = list(client.users.get_users())

    assert len(users) > 0
