"""App Models for the API"""

import enum
from typing import Dict, Optional

import deserialize

from asconnect.models.common import BaseAttributes, Resource, Links, Relationship


class ContentRightsDeclaration(enum.Enum):
    """Contents rights declarations."""

    DOES_NOT_USE_THIRD_PARTY_CONTENT = "DOES_NOT_USE_THIRD_PARTY_CONTENT"
    USES_THIRD_PARTY_CONTENT = "USES_THIRD_PARTY_CONTENT"


@deserialize.key("bundle_id", "bundleId")
@deserialize.key("primary_locale", "primaryLocale")
@deserialize.key("available_in_new_territories", "availableInNewTerritories")
@deserialize.key("content_rights_declaration", "contentRightsDeclaration")
@deserialize.key("is_or_ever_was_made_for_kids", "isOrEverWasMadeForKids")
class AppAttributes(BaseAttributes):
    """Represents app attributes."""

    bundle_id: str
    name: str
    primary_locale: str
    sku: str
    available_in_new_territories: Optional[bool]
    content_rights_declaration: Optional[ContentRightsDeclaration]
    is_or_ever_was_made_for_kids: bool


@deserialize.key("identifier", "id")
class App(Resource):
    """Represents an app."""

    identifier: str
    attributes: AppAttributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links

    @property
    def bundle_id(self) -> str:
        """Return the bundle ID.

        :returns: The bundle ID
        """
        return self.attributes.bundle_id

    @property
    def name(self) -> str:
        """Return the name

        :returns: The name
        """
        return self.attributes.name

    @property
    def primary_locale(self) -> str:
        """Return the primary locale

        :returns: The primary locale
        """
        return self.attributes.primary_locale

    @property
    def sku(self) -> str:
        """Return the SKU

        :returns: The SKU
        """
        return self.attributes.sku

    @property
    def available_in_new_territories(self) -> Optional[bool]:
        """Returns whether or not this app is available in new territories

        :returns: True if this app is available in new territories, False otherwise
        """
        return self.attributes.available_in_new_territories

    @property
    def content_rights_declaration(self) -> Optional[ContentRightsDeclaration]:
        """Return any content rights declaration

        :returns: Any content rights declaration
        """
        return self.attributes.content_rights_declaration

    @property
    def is_or_ever_was_made_for_kids(self) -> bool:
        """Return whether or not this app was ever made for kids

        :returns: True if this app was ever made for kids, False otherwise
        """
        return self.attributes.is_or_ever_was_made_for_kids
