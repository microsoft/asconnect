"""Build beta detail models for the API"""

import enum
from typing import Dict, Optional

import deserialize

from asconnect.models.common import BaseAttributes, Links, Relationship, Resource


class ExternalBetaState(enum.Enum):
    """External beta state."""

    PROCESSING = "PROCESSING"
    PROCESSING_EXCEPTION = "PROCESSING_EXCEPTION"
    MISSING_EXPORT_COMPLIANCE = "MISSING_EXPORT_COMPLIANCE"
    READY_FOR_BETA_TESTING = "READY_FOR_BETA_TESTING"
    IN_BETA_TESTING = "IN_BETA_TESTING"
    EXPIRED = "EXPIRED"
    READY_FOR_BETA_SUBMISSION = "READY_FOR_BETA_SUBMISSION"
    IN_EXPORT_COMPLIANCE_REVIEW = "IN_EXPORT_COMPLIANCE_REVIEW"
    WAITING_FOR_BETA_REVIEW = "WAITING_FOR_BETA_REVIEW"
    IN_BETA_REVIEW = "IN_BETA_REVIEW"
    BETA_REJECTED = "BETA_REJECTED"
    BETA_APPROVED = "BETA_APPROVED"


class InternalBetaState(enum.Enum):
    """Internal beta state."""

    PROCESSING = "PROCESSING"
    PROCESSING_EXCEPTION = "PROCESSING_EXCEPTION"
    MISSING_EXPORT_COMPLIANCE = "MISSING_EXPORT_COMPLIANCE"
    READY_FOR_BETA_TESTING = "READY_FOR_BETA_TESTING"
    IN_BETA_TESTING = "IN_BETA_TESTING"
    EXPIRED = "EXPIRED"
    IN_EXPORT_COMPLIANCE_REVIEW = "IN_EXPORT_COMPLIANCE_REVIEW"


@deserialize.key("identifier", "id")
class BuildBetaDetail(Resource):
    """Represents a build localization."""

    @deserialize.key("auto_notify_enabled", "autoNotifyEnabled")
    @deserialize.key("external_build_state", "externalBuildState")
    @deserialize.key("internal_build_state", "internalBuildState")
    class Attributes(BaseAttributes):
        """Represents beta build localization attributes."""

        auto_notify_enabled: bool
        external_build_state: ExternalBetaState
        internal_build_state: InternalBetaState

    identifier: str
    attributes: Attributes
    relationships: Optional[Dict[str, Relationship]]
    links: Links
