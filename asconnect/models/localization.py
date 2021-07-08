"""Localization models for the API"""

from typing import Dict, Optional

import deserialize

from asconnect.models.common import BaseAttributes, Links, Relationship, Resource


@deserialize.key("identifier", "id")
class BetaAppLocalization(Resource):
    """Represents a build."""

    @deserialize.key("feedback_email", "feedbackEmail")
    @deserialize.key("marketing_url", "marketingUrl")
    @deserialize.key("privacy_policy_url", "privacyPolicyUrl")
    @deserialize.key("tv_os_privacy_policy", "tvOsPrivacyPolicy")
    class Attributes(BaseAttributes):
        """Represents beta app localization attributes."""

        description: str
        feedback_email: str
        locale: str
        marketing_url: Optional[str]
        privacy_policy_url: Optional[str]
        tv_os_privacy_policy: Optional[str]

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links


@deserialize.key("identifier", "id")
class BetaBuildLocalization(Resource):
    """Represents a build localization."""

    @deserialize.key("whats_new", "whatsNew")
    class Attributes(BaseAttributes):
        """Represents beta build localization attributes."""

        locale: str
        whats_new: Optional[str]

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
