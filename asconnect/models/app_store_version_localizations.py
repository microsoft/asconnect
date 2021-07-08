"""App Models for the API"""

from typing import Dict, Optional

import deserialize

from asconnect.models.common import BaseAttributes, Links, Relationship, Resource


@deserialize.key("identifier", "id")
class AppStoreVersionLocalization(Resource):
    """Represents an app store version localization."""

    @deserialize.key("marketing_url", "marketingUrl")
    @deserialize.key("promotional_text", "promotionalText")
    @deserialize.key("support_url", "supportUrl")
    @deserialize.key("whats_new", "whatsNew")
    class Attributes(BaseAttributes):
        """Attributes."""

        description: str
        keywords: str
        locale: str
        marketing_url: Optional[str]
        promotional_text: Optional[str]
        support_url: str
        whats_new: Optional[str]

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
