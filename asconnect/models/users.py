"""User Models for the API"""

import enum
from typing import Dict, List, Optional

import deserialize

from asconnect.models.common import BaseAttributes, Links, Relationship, Resource


class UserRole(enum.Enum):
    """Represents a user role."""

    ACCESS_TO_REPORTS = "ACCESS_TO_REPORTS"
    ACCOUNT_HOLDER = "ACCOUNT_HOLDER"
    ADMIN = "ADMIN"
    APP_MANAGER = "APP_MANAGER"
    CLOUD_MANAGED_APP_DISTRIBUTION = "CLOUD_MANAGED_APP_DISTRIBUTION"
    CLOUD_MANAGED_DEVELOPER_ID = "CLOUD_MANAGED_DEVELOPER_ID"
    CREATE_APPS = "CREATE_APPS"
    CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"
    DEVELOPER = "DEVELOPER"
    FINANCE = "FINANCE"
    IMAGE_MANAGER = "IMAGE_MANAGER"
    MARKETING = "MARKETING"
    SALES = "SALES"


@deserialize.key("first_name", "firstName")
@deserialize.key("last_name", "lastName")
@deserialize.key("provisioning_allowed", "provisioningAllowed")
@deserialize.key("all_apps_visible", "allAppsVisible")
class UserAttributes(BaseAttributes):
    """Represents build attributes."""

    first_name: str
    last_name: str
    roles: List[UserRole]
    provisioning_allowed: bool
    all_apps_visible: bool
    username: str


@deserialize.key("identifier", "id")
class User(Resource):
    """Represents a user."""

    identifier: str
    attributes: UserAttributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
