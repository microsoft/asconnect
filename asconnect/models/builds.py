"""Build Models for the API"""

import deserialize

from asconnect.models.common import BaseAttributes, Links, Relationship, Reprable, Resource


@deserialize.key("template_url", "templateUrl")
class IconAssetToken(Reprable):
    """Represents an icon asset token item."""

    template_url: str
    width: int
    height: int


@deserialize.key("uploaded_date", "uploadedDate")
@deserialize.key("expiration_date", "expirationDate")
@deserialize.key("min_os_version", "minOsVersion")
@deserialize.key("icon_asset_token", "iconAssetToken")
@deserialize.key("processing_state", "processingState")
@deserialize.key("uses_non_exempt_encryption", "usesNonExemptEncryption")
class BuildAttributes(BaseAttributes):
    """Represents build attributes."""

    version: str
    uploaded_date: str
    expiration_date: str
    expired: bool
    min_os_version: str
    icon_asset_token: IconAssetToken | None
    processing_state: str
    uses_non_exempt_encryption: bool | None


@deserialize.key("identifier", "id")
class Build(Resource):
    """Represents a build."""

    identifier: str
    attributes: BuildAttributes
    relationships: dict[str, Relationship] | None
    links: Links
