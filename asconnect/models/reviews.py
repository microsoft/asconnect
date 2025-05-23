"""User Models for the API"""

import datetime

import deserialize

from asconnect.models.common import BaseAttributes, Links, Relationship, Resource


@deserialize.auto_snake()
@deserialize.parser("created_date", datetime.datetime.fromisoformat)
class CustomerReviewAttributes(BaseAttributes):
    """Represents build attributes."""

    body: str
    created_date: datetime.datetime
    rating: int
    reviewer_nickname: str
    title: str
    territory: str


@deserialize.key("identifier", "id")
class CustomerReview(Resource):
    """Represents a user."""

    identifier: str
    attributes: CustomerReviewAttributes
    relationships: dict[str, Relationship] | None
    links: Links
