"""Sorting options."""

import enum


class BuildsSort(enum.Enum):
    """Orders that builds can be sorted."""

    PRE_RELEASE_VERSION = "preReleaseVersion"
    PRE_RELEASE_VERSION_REVERSED = "-preReleaseVersion"
    UPLOADED_DATE = "uploadedDate"
    UPLOADED_DATE_REVERSED = "-uploadedDate"
    VERSION = "version"
    VERSION_REVERSED = "-version"


class CustomerReviewSort(enum.Enum):
    """Orders that customer reviews can be sorted."""

    RATING_ASC = "rating"
    RATING_DESC = "-rating"
    CREATED_DATE_ASC = "createdDate"
    CREATED_DATE_DESC = "-createdDate"
