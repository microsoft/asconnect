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
