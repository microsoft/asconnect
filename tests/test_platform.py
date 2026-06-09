"""Tests for the Platform enum exposed at the package top level.

The top-level `asconnect.Platform` must resolve to the App Store Connect REST
API enum (`asconnect.models.Platform`). Apple rejects the legacy altool-style
lowercase values (e.g. `"ios"`) on endpoints such as `reviewSubmissions` with:

    [409] 'ios' is not a valid value for the attribute 'platform'.
    Expected one of: 'VISION_OS', 'MAC_OS', 'IOS', 'TV_OS'

If anyone re-introduces a duplicate `Platform` enum whose values match altool's
CLI flags, these assertions catch it before it ships.
"""

import asconnect
from asconnect import altool
from asconnect.models import Platform as ModelsPlatform


def test_top_level_platform_is_models_platform() -> None:
    """`asconnect.Platform` must be the App Store Connect API enum."""
    assert asconnect.Platform is ModelsPlatform


def test_platform_values_match_app_store_connect_api() -> None:
    """Values must be the uppercase strings the REST API expects."""
    assert ModelsPlatform.IOS.value == "IOS"
    assert ModelsPlatform.MACOS.value == "MAC_OS"
    assert ModelsPlatform.TVOS.value == "TV_OS"
    assert ModelsPlatform.VISIONOS.value == "VISION_OS"


def test_altool_maps_platform_to_cli_values() -> None:
    """altool's `-t` flag uses different identifiers than the REST API."""
    # This test deliberately asserts the contents of the module-private lookup
    # table that maps the API platform enum to altool's CLI flag values.
    # pylint: disable=protected-access
    assert altool._ALTOOL_PLATFORM_VALUES[ModelsPlatform.IOS] == "ios"
    assert altool._ALTOOL_PLATFORM_VALUES[ModelsPlatform.MACOS] == "osx"
    assert altool._ALTOOL_PLATFORM_VALUES[ModelsPlatform.TVOS] == "appletvos"
    assert altool._ALTOOL_PLATFORM_VALUES[ModelsPlatform.VISIONOS] == "visionos"
