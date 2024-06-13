"""Submission models for the API"""

import deserialize

from asconnect.models.common import BaseAttributes, Resource, Links

@deserialize.key("identifier", "id")
class ReviewSubmission(Resource):
    """Represents an app store review details."""

    @deserialize.key("submitted_date", "submittedDate")
    class Attributes(BaseAttributes):
        """Attributes."""

        platform: str
        state: str
        submitted_date: str

    identifier: str
    attributes: Attributes
    links: Links
