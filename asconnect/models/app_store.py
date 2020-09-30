"""App Models for the API"""

import enum
from typing import Dict, Optional

import deserialize

from asconnect.models.common import Resource, Links, Relationship


class Platform(enum.Enum):
    """The different platforms an app can be for."""

    ios = "IOS"
    macos = "MAC_OS"
    tvos = "TV_OS"


class ReleaseType(enum.Enum):
    """App store release type."""

    manual = "MANUAL"
    after_approval = "AFTER_APPROVAL"
    scheduled = "SCHEDULED"


class AppStoreVersionState(enum.Enum):
    """App store version state."""

    developer_removed_from_sale = "DEVELOPER_REMOVED_FROM_SALE"
    developer_rejected = "DEVELOPER_REJECTED"
    in_review = "IN_REVIEW"
    invalid_binary = "INVALID_BINARY"
    metadata_rejected = "METADATA_REJECTED"
    pending_apple_release = "PENDING_APPLE_RELEASE"
    pending_contract = "PENDING_CONTRACT"
    pending_developer_release = "PENDING_DEVELOPER_RELEASE"
    prepare_for_submission = "PREPARE_FOR_SUBMISSION"
    preorder_ready_for_sale = "PREORDER_READY_FOR_SALE"
    processing_for_app_store = "PROCESSING_FOR_APP_STORE"
    ready_for_sale = "READY_FOR_SALE"
    rejected = "REJECTED"
    removed_from_sale = "REMOVED_FROM_SALE"
    waiting_for_export_compliance = "WAITING_FOR_EXPORT_COMPLIANCE"
    waiting_for_review = "WAITING_FOR_REVIEW"
    replaced_with_new_version = "REPLACED_WITH_NEW_VERSION"


@deserialize.key("identifier", "id")
class AppStoreVersion(Resource):
    """Represents an app store version."""

    @deserialize.key("app_store_state", "appStoreState")
    @deserialize.key("earliest_release_date", "earliestReleaseDate")
    @deserialize.key("release_type", "releaseType")
    @deserialize.key("uses_idfa", "usesIdfa")
    @deserialize.key("version_string", "versionString")
    @deserialize.key("created_date", "createdDate")
    class Attributes:
        """Attributes."""

        platform: Platform
        app_store_state: AppStoreVersionState
        copyright: str
        earliest_release_date: Optional[str]
        release_type: ReleaseType
        uses_idfa: Optional[bool]
        version_string: str
        created_date: str
        downloadable: bool

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links


@deserialize.key("identifier", "id")
class AppStoreReviewDetails(Resource):
    """Represents an app store review details."""

    @deserialize.key("contact_email", "contactEmail")
    @deserialize.key("contact_first_name", "contactFirstName")
    @deserialize.key("contact_last_name", "contactLastName")
    @deserialize.key("contact_phone", "contactPhone")
    @deserialize.key("demo_account_name", "demoAccountName")
    @deserialize.key("demo_account_password", "demoAccountPassword")
    @deserialize.key("demo_account_required", "demoAccountRequired")
    class Attributes:
        """Attributes."""

        contact_email: str
        contact_first_name: str
        contact_last_name: str
        contact_phone: str
        demo_account_name: str
        demo_account_password: str
        demo_account_required: bool
        notes: str

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
