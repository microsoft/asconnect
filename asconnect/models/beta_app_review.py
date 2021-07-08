"""Model types for requests."""

from typing import Dict, Optional

import deserialize

from asconnect.models.common import BaseAttributes, Resource, Links, Relationship


@deserialize.key("identifier", "id")
class BetaAppReviewDetail(Resource):
    """Represents a beta apps review details."""

    @deserialize.key("contact_email", "contactEmail")
    @deserialize.key("contact_first_name", "contactFirstName")
    @deserialize.key("contact_last_name", "contactLastName")
    @deserialize.key("contact_phone", "contactPhone")
    @deserialize.key("demo_account_name", "demoAccountName")
    @deserialize.key("demo_account_password", "demoAccountPassword")
    @deserialize.key("demo_account_required", "demoAccountRequired")
    class Attributes(BaseAttributes):
        """Attributes."""

        contact_email: str
        contact_first_name: str
        contact_last_name: str
        contact_phone: str
        demo_account_name: Optional[str]
        demo_account_password: Optional[str]
        demo_account_required: bool
        notes: Optional[str]

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
