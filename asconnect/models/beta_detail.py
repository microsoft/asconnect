"""Build beta detail models for the API"""

import enum
from typing import Dict, Optional

import deserialize

from asconnect.models.common import Links, Relationship, Resource


class ExternalBetaState(enum.Enum):
    """External beta state."""

    processing = "PROCESSING"
    processing_exception = "PROCESSING_EXCEPTION"
    missing_export_compliance = "MISSING_EXPORT_COMPLIANCE"
    ready_for_beta_testing = "READY_FOR_BETA_TESTING"
    in_beta_testing = "IN_BETA_TESTING"
    expired = "EXPIRED"
    ready_for_beta_submission = "READY_FOR_BETA_SUBMISSION"
    in_export_compliance_review = "IN_EXPORT_COMPLIANCE_REVIEW"
    waiting_for_beta_review = "WAITING_FOR_BETA_REVIEW"
    in_beta_review = "IN_BETA_REVIEW"
    beta_rejected = "BETA_REJECTED"
    beta_approved = "BETA_APPROVED"


class InternalBetaState(enum.Enum):
    """Internal beta state."""

    processing = "PROCESSING"
    processing_exception = "PROCESSING_EXCEPTION"
    missing_export_compliance = "MISSING_EXPORT_COMPLIANCE"
    ready_for_beta_testing = "READY_FOR_BETA_TESTING"
    in_beta_testing = "IN_BETA_TESTING"
    expired = "EXPIRED"
    in_export_compliance_review = "IN_EXPORT_COMPLIANCE_REVIEW"


@deserialize.key("identifier", "id")
class BuildBetaDetail(Resource):
    """Represents a build localization."""

    @deserialize.key("auto_notify_enabled", "autoNotifyEnabled")
    @deserialize.key("external_build_state", "externalBuildState")
    @deserialize.key("internal_build_state", "internalBuildState")
    class Attributes:
        """Represents beta build localization attributes."""

        auto_notify_enabled: bool
        external_build_state: ExternalBetaState
        internal_build_state: InternalBetaState

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
