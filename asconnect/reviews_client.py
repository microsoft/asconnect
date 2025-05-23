"""Wrapper around the Apple App Store Connect APIs."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
from typing import Iterator

from asconnect.httpclient import HttpClient

from asconnect.models import CustomerReview
from asconnect.sorting import CustomerReviewSort
from asconnect.utilities import update_query_parameters


class ReviewsClient:
    """Wrapper class around the ASC API."""

    log: logging.Logger
    http_client: HttpClient

    def __init__(
        self,
        *,
        http_client: HttpClient,
        log: logging.Logger,
    ) -> None:
        """Construct a new client object.

        :param http_client: The API HTTP client
        :param log: Any base logger to be used (one will be created if not supplied)
        """

        self.http_client = http_client
        self.log = log.getChild("reviews")

    def get_reviews(
        self,
        app_id: str,
        sort_order: CustomerReviewSort | None = None,
        territory_filter: list[str] | None = None,
        published_response: bool | None = None,
    ) -> Iterator[CustomerReview]:
        """Get customer reviews for an app.

        :param app_id: The app ID to get reviews for
        :param sort_order: The order to sort the reviews in. Defaults to None.
        :param territory_filter: The territory to filter the reviews by. Defaults to None.
        :param published_response: If set to True, only reviews with a published response will be
                                   returned. If set to False, only reviews without a published
                                   response will be returned. Defaults to None which returns all.

        :yields: An iterator of reviews
        """

        self.log.info("Getting users...")

        url = self.http_client.generate_url(f"apps/{app_id}/customerReviews")

        query_parameters = {}

        if sort_order:
            query_parameters["sort"] = sort_order.value

        if territory_filter:
            if isinstance(territory_filter, str):
                territory_filter = [territory_filter]
            query_parameters["filter[territory]"] = ",".join(territory_filter)

        if published_response is not None:
            query_parameters["exists[publishedResponse]"] = str(published_response).lower()

        url = update_query_parameters(url, query_parameters)

        yield from self.http_client.get(url=url, data_type=list[CustomerReview])
