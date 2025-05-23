# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Tests for the package."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import asconnect  # pylint: disable=wrong-import-order


# pylint: disable=too-many-lines


def test_set_testflight_review_details(client: asconnect.Client, app_id: str) -> None:
    """Test that we can set the testflight app review details."""

    app = client.app.get_from_bundle_id(app_id)

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


def test_get_beta_app_localizations(client: asconnect.Client, app_id: str) -> None:
    """Test get beta app localizations."""

    app = client.app.get_from_bundle_id(app_id)

    assert app is not None

    client.beta_review.get_beta_app_localizations(app.identifier)


def test_set_testflight_localized_review_details(client: asconnect.Client, app_id: str) -> None:
    """Test that we can set the testflight app review details."""

    app = client.app.get_from_bundle_id(app_id)

    assert app is not None

    info = {
        "en-US": {
            "feedbackEmail": "j.doe@example.com",
            "description": "Thanks for helping us test!",
        }
    }

    client.beta_review.set_beta_app_localizations(app.identifier, info)


def test_get_build_localization_details(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get a builds localization details."""

    build = client.build.get_from_build_number(build_number="", bundle_id=app_id)

    assert build is not None

    assert len(list(client.beta_review.get_beta_build_localizations(build.identifier))) > 0


def test_set_whats_new(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get a builds localization details."""

    build = client.build.get_from_build_number(build_number="", bundle_id=app_id)

    assert build is not None

    client.beta_review.set_whats_new_for_build(
        build.identifier,
        {"en-US": "Bug fixes and performance improvements"},
    )


def test_get_beta_groups_detail(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get a builds beta details."""

    app = client.app.get_from_bundle_id(app_id)

    assert app is not None

    groups = [
        group
        for group in client.beta_review.get_beta_groups(app.identifier)
        if group.attributes.name in ["External Testers", "Public Link Testers"]
    ]

    assert len(groups) == 2


def test_set_beta_groups_detail(client: asconnect.Client, app_id: str) -> None:
    """Test that we can get a builds beta details."""

    app = client.app.get_from_bundle_id(app_id)

    assert app is not None

    build = client.build.get_from_build_number(build_number="", bundle_id=app_id)

    assert build is not None

    groups = [
        group
        for group in client.beta_review.get_beta_groups(app.identifier)
        if group.attributes.name in ["External Testers", "Public Link Testers"]
    ]

    client.beta_review.set_beta_groups_on_build(build.identifier, groups)


def test_beta_review_submission(client: asconnect.Client, app_id: str) -> None:
    """Test that we can submit a build for beta review."""

    build = client.build.get_from_build_number(build_number="", bundle_id=app_id)

    assert build is not None

    client.beta_review.submit_for_beta_review(build.identifier)
