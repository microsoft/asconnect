"""App Models for the API"""

import enum
from typing import Dict, Optional

import deserialize

from asconnect.models.common import BaseAttributes, Links, Relationship, Resource


class Platform(enum.Enum):
    """The different platforms an app can be for."""

    IOS = "IOS"
    MACOS = "MAC_OS"
    TVOS = "TV_OS"


class ReleaseType(enum.Enum):
    """App store release type."""

    MANUAL = "MANUAL"
    AFTER_APPROVAL = "AFTER_APPROVAL"
    SCHEDULED = "SCHEDULED"


class PhasedReleaseState(enum.Enum):
    """App store phased release state.

    inactive: initial state
    active: over the course of 7 days the app will be rolled out in randomly selected phases
    paused: the rollout is paused
    complete: the rollout is complete
    """

    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETE = "COMPLETE"


class AppStoreVersionState(enum.Enum):
    """App store version state."""

    DEVELOPER_REMOVED_FROM_SALE = "DEVELOPER_REMOVED_FROM_SALE"
    DEVELOPER_REJECTED = "DEVELOPER_REJECTED"
    IN_REVIEW = "IN_REVIEW"
    INVALID_BINARY = "INVALID_BINARY"
    METADATA_REJECTED = "METADATA_REJECTED"
    PENDING_APPLE_RELEASE = "PENDING_APPLE_RELEASE"
    PENDING_CONTRACT = "PENDING_CONTRACT"
    PENDING_DEVELOPER_RELEASE = "PENDING_DEVELOPER_RELEASE"
    PREPARE_FOR_SUBMISSION = "PREPARE_FOR_SUBMISSION"
    PREORDER_READY_FOR_SALE = "PREORDER_READY_FOR_SALE"
    PROCESSING_FOR_APP_STORE = "PROCESSING_FOR_APP_STORE"
    READY_FOR_SALE = "READY_FOR_SALE"
    REJECTED = "REJECTED"
    REMOVED_FROM_SALE = "REMOVED_FROM_SALE"
    WAITING_FOR_EXPORT_COMPLIANCE = "WAITING_FOR_EXPORT_COMPLIANCE"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"
    REPLACED_WITH_NEW_VERSION = "REPLACED_WITH_NEW_VERSION"


@deserialize.key("identifier", "id")
class AppStoreVersion(Resource):
    """Represents an app store version."""

    @deserialize.key("app_store_state", "appStoreState")
    @deserialize.key("earliest_release_date", "earliestReleaseDate")
    @deserialize.key("release_type", "releaseType")
    @deserialize.key("uses_idfa", "usesIdfa")
    @deserialize.key("version_string", "versionString")
    @deserialize.key("created_date", "createdDate")
    class Attributes(BaseAttributes):
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
class AppStoreVersionPhasedRelease(Resource):
    """Represents an app store phased release."""

    @deserialize.key("current_day_number", "currentDayNumber")
    @deserialize.key("phased_release_state", "phasedReleaseState")
    @deserialize.key("start_date", "startDate")
    @deserialize.key("total_pause_duration", "totalPauseDuration")
    class Attributes(BaseAttributes):
        """Attributes."""

        current_day_number: int
        phased_release_state: PhasedReleaseState
        start_date: Optional[str]
        total_pause_duration: int

    identifier: str
    attributes: Attributes
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
    class Attributes(BaseAttributes):
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
