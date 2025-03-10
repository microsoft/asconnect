"""Localization models for the API"""

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
        marketing_url: str | None
        privacy_policy_url: str | None
        tv_os_privacy_policy: str | None

    identifier: str
    attributes: Attributes
    relationships: dict[str, Relationship] | None
    links: Links


@deserialize.key("identifier", "id")
class BetaBuildLocalization(Resource):
    """Represents a build localization."""

    @deserialize.key("whats_new", "whatsNew")
    class Attributes(BaseAttributes):
        """Represents beta build localization attributes."""

        locale: str
        whats_new: str | None

    identifier: str
    attributes: Attributes
    relationships: dict[str, Relationship] | None
    links: Links
