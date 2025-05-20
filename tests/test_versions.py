# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Tests for the package."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import asconnect  # pylint: disable=wrong-import-order


# pylint: disable=too-many-lines


def test_create_new_phased_release(client: asconnect.Client, app_id: str) -> None:
    """Test that we can create a new app store version."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    version = client.app.create_new_version(version="1.2.3", app_id=app.identifier)
    release = client.version.create_phased_release(version_id=version.identifier)

    assert release is not None
    assert release.attributes.phased_release_state is asconnect.models.PhasedReleaseState.INACTIVE


def test_get_versions(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get app store versions."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    versions = list(client.version.get_all(app_id=app.identifier))
    assert len(versions) > 0


def test_get_version(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get a specific app store version."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None


def test_get_version_localizations(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get a specific app store version."""

    app = client.app.get_from_bundle_id(app_id)
    assert app is not None

    version = client.version.get_version(app_id=app.identifier, version_string="1.2.3")
    assert version is not None

    localizations = list(client.version.get_localizations(version_id=version.identifier))
    assert len(localizations) > 0


def test_get_app_info_localization(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get app info localization."""

    app = client.app.get_from_bundle_id(app_id)
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


def test_set_idfa(client: asconnect.Client) -> None:
    """Set the advertising ID declaration"""

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


def test_get_versions_phased_release(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get a specific app store version."""

    app = client.app.get_from_bundle_id(app_id)

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
    localized_info: (
        asconnect.models.AppInfoLocalization | asconnect.models.AppStoreVersionLocalization
    ),
    current_value: str | None,
    version: str | None = None,
) -> str | None:
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
