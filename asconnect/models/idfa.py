"""App Models for the API"""

from typing import Dict, Optional

import deserialize

from asconnect.models.common import BaseAttributes, Resource, Links, Relationship


@deserialize.key("identifier", "id")
class IdfaDeclaration(Resource):
    """Represents an IDFA declaration."""

    @deserialize.key("attributes_action_with_previous_ad", "attributesActionWithPreviousAd")
    @deserialize.key(
        "attributes_app_installation_to_previous_ad", "attributesAppInstallationToPreviousAd"
    )
    @deserialize.key("honors_limited_ad_tracking", "honorsLimitedAdTracking")
    @deserialize.key("serves_ads", "servesAds")
    class Attributes(BaseAttributes):
        """Attributes."""

        attributes_action_with_previous_ad: bool
        attributes_app_installation_to_previous_ad: bool
        honors_limited_ad_tracking: bool
        serves_ads: bool

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
