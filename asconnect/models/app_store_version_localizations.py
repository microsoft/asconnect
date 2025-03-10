"""App Models for the API"""

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

        description: str | None
        keywords: str | None
        locale: str
        marketing_url: str | None
        promotional_text: str | None
        support_url: str | None
        whats_new: str | None

    identifier: str
    attributes: Attributes
    relationships: dict[str, Relationship] | None
    links: Links
