"""Utilities for the library."""

import hashlib
from typing import Dict, Iterator, Optional, TypeVar
import urllib.parse

IteratorType = TypeVar("IteratorType")


def next_or_none(iterator: Iterator[IteratorType]) -> Optional[IteratorType]:
    """Get the next value from an iterator, or return None when it is exhausted.

    :param iterator: The iterator to get the next value from

    :returns: The next value or None if exhausted
    """
    try:
        return next(iterator)
    except StopIteration:
        return None


def update_query_parameters(url: str, query_parameters: Dict[str, str]) -> str:
    """Update the query parameters on a URL.

    :param url: The URL to update
    :param query_parameters: The query parameters to add

    :returns: The updated URL
    """
    parsed_url = urllib.parse.urlparse(url)
    parsed_parameters = dict(urllib.parse.parse_qsl(parsed_url.query))

    new_parameters = {**parsed_parameters, **query_parameters}
    new_parameter_string = urllib.parse.urlencode(new_parameters, safe="[]")

    parsed_url = urllib.parse.ParseResult(**dict(parsed_url._asdict(), query=new_parameter_string))

    return urllib.parse.urlunparse(parsed_url)


def md5_file(file_path: str) -> str:
    """Generate the MD5 of a file.

    :param file_path: The file to generate the MD5 for

    :returns: The MD5 as a hex string
    """
    hasher = hashlib.md5()
    with open(file_path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
