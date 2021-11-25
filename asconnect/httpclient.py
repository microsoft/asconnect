"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import datetime
import logging
from typing import Any, Dict, Iterator, Optional, Tuple, Type

import deserialize
import jwt
import requests

from asconnect.exceptions import AppStoreConnectError

NEW_TOKEN_AGE_IN_MINUTES = 15
MINIMUM_TOKEN_AGE = 5


class HttpClient:
    """Base HTTP client for the ASC API."""

    _key_id: str
    _key_contents: str
    _issuer_id: str
    log: logging.Logger

    _credentials_valid: bool
    _cached_token_info: Optional[Tuple[str, datetime.datetime]]

    def __init__(
        self,
        *,
        key_id: str,
        key_contents: str,
        issuer_id: str,
        log: logging.Logger,
    ) -> None:
        """Construct a new client object.

        :param key_id: The ID of your key (can be found in app store connect)
        :param key_contents: The contents of your key
        :param issuer_id: The contents of your key (can be found in app store connect
        :param log: Any base logger to be used (one will be created if not supplied)
        """

        self._key_id = key_id
        self._key_contents = key_contents
        self._issuer_id = issuer_id
        self._credentials_valid = False
        self.log = log.getChild("http")

        self._cached_token_info = None

    @property
    def key_contents(self) -> str:
        """Get key contents.

        :returns: Key contents
        """
        return self._key_contents

    @key_contents.setter
    def key_contents(self, value: str) -> None:
        """Set key contents.

        :param value: The new value to set to
        """
        self._key_contents = value
        self._credentials_valid = False

    @property
    def key_id(self) -> str:
        """Get key ID.

        :returns: Key ID
        """
        return self._key_id

    @key_id.setter
    def key_id(self, value: str) -> None:
        """Set key ID.

        :param value: The new value to set to
        """
        self._key_id = value
        self._credentials_valid = False

    @property
    def issuer_id(self) -> str:
        """Get issuer ID.

        :returns: Issuer ID
        """
        return self._issuer_id

    @issuer_id.setter
    def issuer_id(self, value: str) -> None:
        """Set issuer ID.

        :param value: The new value to set to
        """
        self._issuer_id = value
        self._credentials_valid = False

    def generate_token(self) -> str:
        """Generate a new JWT token.

        :returns: The JWT token as a string
        """

        # Apple state that performance is improved if we re-use the same token
        # instead of generating a new one each time
        if self._cached_token_info is not None:
            cached_token, cached_expiration = self._cached_token_info
            # Only return a token with time remaining on it
            if cached_expiration - datetime.datetime.now() > datetime.timedelta(
                minutes=MINIMUM_TOKEN_AGE
            ):
                self.log.debug(f"Using cached token. Expiration time: {cached_expiration}")
                return cached_token

            self._cached_token_info = None

        # Tokens more than 20 minutes in the future are invalid, so our new one is less than that
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=NEW_TOKEN_AGE_IN_MINUTES)

        # Details at https://developer.apple.com/documentation/appstoreconnectapi/generating_tokens_for_api_requests
        token = jwt.encode(
            {
                "iss": self.issuer_id,
                "exp": int(expiration.timestamp()),
                "aud": "appstoreconnect-v1",
            },
            self.key_contents,
            algorithm="ES256",
            headers={"kid": self.key_id, "typ": "JWT"},
        ).decode("utf-8")

        self.log.debug(f"Generating new token. Expiration: {expiration}")
        self._cached_token_info = (token, expiration)

        return token

    def generate_url(self, endpoint: str) -> str:
        """Generate a URL for an endpoint.

        :param endpoint: The endpoint to generate the URL for

        :returns: An endpoint URL
        """
        _ = self
        return f"https://api.appstoreconnect.apple.com/v1/{endpoint}"

    def verify_response(self, response: requests.Response) -> None:
        """Perform some checks on the response.

        :param response: The response to check
        """
        if response.status_code >= 200 and response.status_code < 300:
            self._credentials_valid = True

    def get(
        self,
        *,
        data_type: Type,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        attempts: int = 3,
    ) -> Iterator[Any]:
        """Perform a GET to the endpoint specified.

        Either endpoint or url must be specified. url will take precedence if
        both are specified.

        :param Type data_type: The class to deserialize the data of the response to
        :param Optional[str] endpoint: The endpoint to perform the GET on
        :param Optional[str] url: The full URL to perform the GET on
        :param int attempts: Number of attempts remaining to try this call

        :raises ValueError: If neither url or endpoint are specified
        :raises AppStoreConnectError: If an error with the API occurs

        :returns: The raw response
        """
        token = self.generate_token()

        if url is None:
            if endpoint is None:
                raise ValueError("Either `endpoint` or `url` must be set")
            url = self.generate_url(endpoint)

        iterations = 0

        while True:
            iterations += 1

            raw_response = requests.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )

            self.verify_response(raw_response)

            try:
                response_data = self.extract_data(raw_response)
            except AppStoreConnectError as ex:
                if attempts > 1 and (
                    ex.response.status_code >= 500
                    or (ex.response.status_code == 401 and self._credentials_valid)
                ):
                    yield from self.get(
                        data_type=data_type, endpoint=endpoint, url=url, attempts=attempts - 1
                    )
                    return

                raise

            if response_data["data"] is None:
                yield from []
            else:
                deserialized_data = deserialize.deserialize(data_type, response_data["data"])

                if isinstance(deserialized_data, list):
                    yield from deserialized_data
                else:
                    yield deserialized_data

            if response_data.get("links") is None:
                break

            if response_data["links"].get("next") is None:
                break

            url = response_data["links"]["next"]
            assert url is not None

        # This is only used for debugging, so we just assert so it isn't flagged as unused
        assert iterations != 0

    def patch(
        self,
        *,
        data_type: Optional[Type],
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        data: Any,
    ) -> Any:
        """Perform a PATCH to the endpoint specified.

        Either endpoint or url must be specified. url will take precedence if
        both are specified.

        :param Optional[Type] data_type: The class to deserialize the data of the response to
        :param Optional[str] endpoint: The endpoint to perform the GET on
        :param Optional[str] url: The full URL to perform the GET on
        :param Any data: Some JSON serializable data to send

        :raises AppStoreConnectError: If we don't get a 200 response back
        :raises ValueError: If neither url or endpoint are specified

        :returns: The raw response
        """
        token = self.generate_token()

        if url is None:
            if endpoint is None:
                raise ValueError("Either `endpoint` or `url` must be set")
            url = self.generate_url(endpoint)

        raw_response = requests.patch(
            url,
            json=data,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )

        self.verify_response(raw_response)

        if raw_response.status_code == 204:
            return None

        if raw_response.status_code != 200:
            raise AppStoreConnectError(raw_response)

        response_data = self.extract_data(raw_response)

        if data_type is None:
            return None

        return deserialize.deserialize(data_type, response_data["data"])

    def post(
        self,
        *,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        data: Any,
        data_type: Optional[Type] = None,
    ) -> Any:
        """Perform a POST to the endpoint specified.

        Either endpoint or url must be specified. url will take precedence if
        both are specified.

        :param Optional[str] endpoint: The endpoint to perform the GET on
        :param Optional[str] url: The full URL to perform the GET on
        :param Any data: Some JSON serializable data to send
        :param Optional[Type] data_type: The data type to deserialize the response to

        :raises ValueError: If neither url or endpoint are specified
        :raises AppStoreConnectError: If we get a failure response back from the API

        :returns: The raw response
        """
        token = self.generate_token()

        if url is None:
            if endpoint is None:
                raise ValueError("Either `endpoint` or `url` must be set")
            url = self.generate_url(endpoint)

        raw_response = requests.post(
            url,
            json=data,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )

        self.verify_response(raw_response)

        if raw_response.status_code == 201:

            if data_type is None:
                return None

            response_data = self.extract_data(raw_response)

            return deserialize.deserialize(data_type, response_data["data"])

        if raw_response.status_code >= 200 and raw_response.status_code < 300:
            return None

        raise AppStoreConnectError(raw_response)

    def delete(
        self, *, endpoint: Optional[str] = None, url: Optional[str] = None
    ) -> requests.Response:
        """Perform a DELETE to the endpoint specified.

        Either endpoint or url must be specified. url will take precedence if
        both are specified.

        :param Optional[str] endpoint: The endpoint to perform the GET on
        :param Optional[str] url: The full URL to perform the GET on

        :raises ValueError: If neither url or endpoint are specified

        :returns: The raw response
        """
        token = self.generate_token()

        if url is None:
            if endpoint is None:
                raise ValueError("Either `endpoint` or `url` must be set")
            url = self.generate_url(endpoint)

        raw_response = requests.delete(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )

        self.verify_response(raw_response)

        return raw_response

    def put_chunk(
        self, *, url: str, additional_headers: Dict[str, str], data: bytes
    ) -> requests.Response:
        """Perform a PUT to the url specified

        :param str url: The full URL to perform the PUT on
        :param Dict[str,str] additional_headers: The additional headers to add
        :param bytes data: The raw data to upload

        :returns: The raw response
        """
        token = self.generate_token()

        headers = {
            **{"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            **additional_headers,
        }

        raw_response = requests.put(url=url, data=data, headers=headers)

        self.verify_response(raw_response)

        return raw_response

    def extract_data(self, response: requests.Response) -> Any:
        """Validate a response from the API and extract the data

        :param response: The response to validate

        :raises AppStoreConnectError: On any failure to validate

        :returns: Any data in the response
        """
        _ = self

        if not response.ok:
            raise AppStoreConnectError(response)

        return response.json()
