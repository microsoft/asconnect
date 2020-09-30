"""App Models for the API"""

import enum
from typing import Dict, List, Optional

import deserialize

from asconnect.models.common import Resource, Links, Relationship


class ScreenshotDisplayType(enum.Enum):
    """Screenshot display type."""

    app_iphone_65 = "APP_IPHONE_65"
    app_iphone_58 = "APP_IPHONE_58"
    app_iphone_55 = "APP_IPHONE_55"
    app_iphone_47 = "APP_IPHONE_47"
    app_iphone_40 = "APP_IPHONE_40"
    app_iphone_35 = "APP_IPHONE_35"
    app_ipad_pro_3gen_129 = "APP_IPAD_PRO_3GEN_129"
    app_ipad_pro_3gen_11 = "APP_IPAD_PRO_3GEN_11"
    app_ipad_pro_129 = "APP_IPAD_PRO_129"
    app_ipad_105 = "APP_IPAD_105"
    app_ipad_97 = "APP_IPAD_97"
    app_desktop = "APP_DESKTOP"
    app_watch_series_4 = "APP_WATCH_SERIES_4"
    app_watch_series_3 = "APP_WATCH_SERIES_3"
    app_apple_tv = "APP_APPLE_TV"
    imessage_app_iphone_65 = "IMESSAGE_APP_IPHONE_65"
    imessage_app_iphone_58 = "IMESSAGE_APP_IPHONE_58"
    imessage_app_iphone_55 = "IMESSAGE_APP_IPHONE_55"
    imessage_app_iphone_47 = "IMESSAGE_APP_IPHONE_47"
    imessage_app_iphone_40 = "IMESSAGE_APP_IPHONE_40"
    imessage_app_ipad_pro_3gen_129 = "IMESSAGE_APP_IPAD_PRO_3GEN_129"
    imessage_app_ipad_pro_3gen_11 = "IMESSAGE_APP_IPAD_PRO_3GEN_11"
    imessage_app_ipad_pro_129 = "IMESSAGE_APP_IPAD_PRO_129"
    imessage_app_ipad_105 = "IMESSAGE_APP_IPAD_105"
    imessage_app_ipad_97 = "IMESSAGE_APP_IPAD_97"

    @staticmethod
    def from_name(name: str) -> "ScreenshotDisplayType":
        """Generate the display type from an image name.

        :param name: The name to convert

        :returns: The corresponding display type
        """
        identifier = name.split("-")[0]
        return ScreenshotDisplayType(identifier)


@deserialize.key("identifier", "id")
class AppScreenshotSet(Resource):
    """Represents an app store screenshot set."""

    @deserialize.key("screenshot_display_type", "screenshotDisplayType")
    class Attributes:
        """Attributes."""

        screenshot_display_type: ScreenshotDisplayType

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links


class AppMediaStateError:
    """An app media state error."""

    code: str
    description: str


class AppMediaAssetStateState(enum.Enum):
    """The state value for and app media asset state."""

    awaiting_upload = "AWAITING_UPLOAD"
    upload_complete = "UPLOAD_COMPLETE"
    complete = "COMPLETE"
    failed = "FAILED"


class AppMediaAssetState:
    """An app media asset state."""

    errors: List[AppMediaStateError]
    state: AppMediaAssetStateState
    warnings: Optional[List[AppMediaStateError]]


@deserialize.key("template_url", "templateUrl")
class ImageAsset:
    """An image asset."""

    template_url: str
    height: int
    width: int


class UploadOperationHeader:
    """An upload operation header."""

    name: str
    value: str


@deserialize.key("request_headers", "requestHeaders")
class UploadOperation:
    """An upload operation."""

    length: int
    method: str
    offset: int
    request_headers: List[UploadOperationHeader]
    url: str


@deserialize.key("identifier", "id")
class AppScreenshot(Resource):
    """Represents an app store screenshot."""

    @deserialize.key("asset_delivery_state", "assetDeliveryState")
    @deserialize.key("asset_token", "assetToken")
    @deserialize.key("asset_type", "assetType")
    @deserialize.key("file_name", "fileName")
    @deserialize.key("file_size", "fileSize")
    @deserialize.key("image_asset", "imageAsset")
    @deserialize.key("source_file_checksum", "sourceFileChecksum")
    @deserialize.key("upload_operations", "uploadOperations")
    class Attributes:
        """Attributes."""

        asset_delivery_state: AppMediaAssetState
        asset_token: str
        asset_type: str
        file_name: str
        file_size: int
        image_asset: Optional[ImageAsset]
        source_file_checksum: Optional[str]
        uploaded: Optional[bool]
        upload_operations: Optional[List[UploadOperation]]

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
