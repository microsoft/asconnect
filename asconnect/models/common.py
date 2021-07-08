"""Models for the API"""

from typing import Optional

import deserialize


@deserialize.key("self_link", "self")
class Links:
    """Represents item links."""

    self_link: Optional[str]
    first: Optional[str]
    next: Optional[str]
    related: Optional[str]


class Relationship:
    """Represents a relationship."""

    links: Links


class Paging:
    """Represents a paging data item in a REST response."""

    total: int
    limit: int


class Meta:
    """Represents a meta data item in a REST response."""

    paging: Paging


class Reprable:
    """Something that can be automatically repr'd."""

    def __repr__(self) -> str:
        """Generate and return the repl representation of the object.

        :return: A repl representation of the object
        """
        properties = {}
        for attribute_name in dir(self):
            if attribute_name.startswith("__"):
                continue
            properties[attribute_name] = getattr(self, attribute_name)
        return str(properties)


@deserialize.key("resource_type", "type")
class Resource(Reprable):
    """Represents a resource."""

    resource_type: str


class BaseAttributes(Reprable):
    """Represents base attributes."""
