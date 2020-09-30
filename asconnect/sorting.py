"""Sorting options."""

import enum


class BuildsSort(enum.Enum):
    """Orders that builds can be sorted."""

    PreReleaseVersion = "preReleaseVersion"
    PreReleaseVersionReversed = "-preReleaseVersion"
    UploadedDate = "uploadedDate"
    UploadedDateReversed = "-uploadedDate"
    Version = "version"
    VersionReversed = "-version"
