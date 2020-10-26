"""Localization models for the API"""

import enum
from typing import Dict, Optional

import deserialize

from asconnect.models.common import Links, Relationship, Resource
from asconnect.models.app_store import AppStoreVersionState


@deserialize.key("identifier", "id")
class AppInfoLocalization(Resource):
    """Represents a build."""

    @deserialize.key("privacy_policy_text", "privacyPolicyText")
    @deserialize.key("privacy_policy_url", "privacyPolicyUrl")
    class Attributes:
        """Represents app info localization attributes."""

        locale: Optional[str]
        name: Optional[str]
        privacy_policy_text: Optional[str]
        privacy_policy_url: Optional[str]
        subtitle: Optional[str]

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links


class AppStoreAgeRating(enum.Enum):
    """App store age rating."""

    four_plus = "FOUR_PLUS"
    nine_plus = "NINE_PLUS"
    twelve_plus = "TWELVE_PLUS"
    seventeen_plus = "SEVENTEEN_PLUS"


class BrazilAgeRating(enum.Enum):
    """Brazil age rating."""

    l = "L"
    ten = "TEN"
    twelve = "TWELVE"
    fourteen = "FOURTEEN"
    sixteen = "SIXTEEN"
    eighteen = "EIGHTEEN"


class KidsAgeBand(enum.Enum):
    """Kids age band."""

    five_and_under = "FIVE_AND_UNDER"
    six_to_eight = "SIX_TO_EIGHT"
    nine_to_eleven = "NINE_TO_ELEVEN"


@deserialize.key("identifier", "id")
class AppInfo(Resource):
    """Represents an apps info."""

    @deserialize.key("app_store_age_rating", "appStoreAgeRating")
    @deserialize.key("app_store_state", "appStoreState")
    @deserialize.key("brazil_age_rating", "brazilAgeRating")
    @deserialize.key("kids_age_band", "kidsAgeBand")
    class Attributes:
        """Represents app info localization attributes."""

        app_store_age_rating: AppStoreAgeRating
        app_store_state: AppStoreVersionState
        brazil_age_rating: BrazilAgeRating
        kids_age_band: Optional[KidsAgeBand]

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
