"""Review submission models for the API"""

import enum

import deserialize

from asconnect.models.app_store import Platform
from asconnect.models.common import BaseAttributes, Links, Relationship, Resource


class ReviewSubmissionState(enum.Enum):
    """The state of a review submission.

    A freshly created submission is in ``READY_FOR_REVIEW`` (a draft that has
    not yet been submitted). Setting ``submitted`` to ``True`` moves it to
    ``WAITING_FOR_REVIEW`` and from there into Apple's review pipeline.

    Apple defines *seven* states. ``COMPLETING`` is the transient state the API
    reports while a finished submission is being wrapped up (between
    ``CANCELING``/review and ``COMPLETE``). It must be modelled here even though
    we never set it: ``ReviewSubmission.Attributes.state`` is a strict enum, so
    an unlisted value returned by a list query raises ``DeserializeException``
    (which is *not* an ``AppStoreConnectError`` and therefore bypasses the
    retry handling) and crashes the open-submission lookup.
    """

    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"
    IN_REVIEW = "IN_REVIEW"
    UNRESOLVED_ISSUES = "UNRESOLVED_ISSUES"
    CANCELING = "CANCELING"
    COMPLETING = "COMPLETING"
    COMPLETE = "COMPLETE"


@deserialize.key("identifier", "id")
class ReviewSubmission(Resource):
    """Represents a review submission.

    A review submission is the container Apple uses to submit one or more
    ``appStoreVersion`` (and other reviewable items) for App Review. Only one
    non-``COMPLETE`` submission may exist per app at a time.
    """

    class Attributes(BaseAttributes):
        """Attributes."""

        platform: Platform
        state: ReviewSubmissionState

    identifier: str
    attributes: Attributes
    relationships: dict[str, Relationship] | None
    links: Links


@deserialize.key("resource_type", "type")
@deserialize.key("identifier", "id")
class ResourceLinkage:
    """A JSON:API resource linkage.

    This is the ``{"type": ..., "id": ...}`` pointer that appears in a
    relationship's ``data`` member and identifies the related resource without
    having to follow its link.
    """

    resource_type: str
    identifier: str


class LinkageRelationship:
    """A relationship that may expose its resource linkage (``data``).

    The shared :class:`~asconnect.models.common.Relationship` only models
    ``links``, which is enough to *follow* a related URL but not to learn
    *which* resource is on the other end. Review submission items need that
    identity - to tell which app store version an item references - so this
    variant also parses the optional ``data`` pointer. Both members are
    optional because Apple only populates ``data`` for relationships that were
    requested via ``include``.
    """

    data: ResourceLinkage | None
    links: Links | None


@deserialize.key("identifier", "id")
class ReviewSubmissionItem(Resource):
    """Represents a single item (e.g. an app store version) in a review submission.

    When the containing list is fetched with ``include=appStoreVersion``, the
    ``appStoreVersion`` relationship carries a ``data`` linkage identifying the
    attached version.
    """

    identifier: str
    relationships: dict[str, LinkageRelationship] | None
    links: Links
