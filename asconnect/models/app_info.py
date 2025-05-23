"""Localization models for the API"""

import enum

import deserialize

from asconnect.models.common import BaseAttributes, Links, Relationship, Resource
from asconnect.models.app_store import AppStoreVersionState


@deserialize.key("identifier", "id")
class AppInfoLocalization(Resource):
    """Represents a build."""

    @deserialize.key("privacy_policy_text", "privacyPolicyText")
    @deserialize.key("privacy_policy_url", "privacyPolicyUrl")
    class Attributes(BaseAttributes):
        """Represents app info localization attributes."""

        locale: str | None
        name: str | None
        privacy_policy_text: str | None
        privacy_policy_url: str | None
        subtitle: str | None

    identifier: str
    attributes: Attributes
    relationships: dict[str, Relationship] | None
    links: Links


class AppStoreAgeRating(enum.Enum):
    """App store age rating."""

    FOUR_PLUS = "FOUR_PLUS"
    NINE_PLUS = "NINE_PLUS"
    TWELVE_PLUS = "TWELVE_PLUS"
    SEVENTEEN_PLUS = "SEVENTEEN_PLUS"


class BrazilAgeRating(enum.Enum):
    """Brazil age rating."""

    L = "L"
    TEN = "TEN"
    TWELVE = "TWELVE"
    FOURTEEN = "FOURTEEN"
    SIXTEEN = "SIXTEEN"
    EIGHTEEN = "EIGHTEEN"


class KidsAgeBand(enum.Enum):
    """Kids age band."""

    FIVE_AND_UNDER = "FIVE_AND_UNDER"
    SIX_TO_EIGHT = "SIX_TO_EIGHT"
    NINE_TO_ELEVEN = "NINE_TO_ELEVEN"


@deserialize.key("identifier", "id")
class AppInfo(Resource):
    """Represents an apps info."""

    @deserialize.key("app_store_age_rating", "appStoreAgeRating")
    @deserialize.key("app_store_state", "appStoreState")
    @deserialize.key("brazil_age_rating", "brazilAgeRating")
    @deserialize.key("kids_age_band", "kidsAgeBand")
    class Attributes(BaseAttributes):
        """Represents app info localization attributes."""

        app_store_age_rating: AppStoreAgeRating
        app_store_state: AppStoreVersionState
        brazil_age_rating: BrazilAgeRating | None
        kids_age_band: KidsAgeBand | None

    identifier: str
    attributes: Attributes
    relationships: dict[str, Relationship] | None
    links: Links
