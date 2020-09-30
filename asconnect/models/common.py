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


@deserialize.key("resource_type", "type")
class Resource:
    """Represents a resource."""

    resource_type: str
