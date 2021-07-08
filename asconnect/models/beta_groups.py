"""Beta groups models for the API"""

from typing import Dict, Optional

import deserialize

from asconnect.models.common import BaseAttributes, Links, Relationship, Resource


@deserialize.key("identifier", "id")
class BetaGroup(Resource):
    """Represents a beta group."""

    @deserialize.key("is_internal_group", "isInternalGroup")
    @deserialize.key("public_link", "publicLink")
    @deserialize.key("public_link_enabled", "publicLinkEnabled")
    @deserialize.key("public_link_id", "publicLinkId")
    @deserialize.key("public_link_limit", "publicLinkLimit")
    @deserialize.key("public_link_limit_enabled", "publicLinkLimitEnabled")
    @deserialize.key("created_date", "createdDate")
    @deserialize.key("feedback_enabled", "feedbackEnabled")
    class Attributes(BaseAttributes):
        """Represents beta group attributes."""

        is_internal_group: bool
        name: str
        public_link: Optional[str]
        public_link_enabled: Optional[bool]
        public_link_id: Optional[str]
        public_link_limit: Optional[int]
        public_link_limit_enabled: Optional[bool]
        created_date: str
        feedback_enabled: bool

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
