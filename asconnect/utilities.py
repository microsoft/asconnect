"""Utilities for the library."""

import hashlib
import os
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


def write_key(key_id: str, key_contents: str) -> str:
    """Write a key to the private key folder for altool.

    :param key_id: The ID of the key
    :param key_contents: The text key contents

    :returns: The path the key was written out to
    """

    folder_path = os.path.expanduser("~/.appstoreconnect/private_keys")
    os.makedirs(folder_path, exist_ok=True)

    key_file_name = f"AuthKey_{key_id}.p8"
    key_file_path = os.path.join(folder_path, key_file_name)

    with open(key_file_path, "w") as key_file:
        key_file.write(key_contents)

    return key_file_path
