"""Unit tests for the review submission flow.

These tests exercise the orchestration in ``VersionClient.submit_for_review``
against a mocked HTTP client, so they require no credentials and never touch
Apple. They verify that the full three-step ``reviewSubmissions`` flow (create
-> add item -> mark submitted) is performed in order, that an existing
submission is reused rather than duplicated, that the version actually attached
is the one requested, and that the post-submit state is taken from the PATCH
response.
"""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
import os
import sys
from unittest import mock

import deserialize
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from asconnect.exceptions import (
    AppStoreConnectError,
)  # pylint: disable=wrong-import-position
from asconnect.version_client import (
    VersionClient,
)  # pylint: disable=wrong-import-position
from asconnect.models import (  # pylint: disable=wrong-import-position
    Platform,
    ReviewSubmission,
    ReviewSubmissionItem,
    ReviewSubmissionState,
)


APP_ID = "app-123"
VERSION_ID = "version-456"
SUBMISSION_ID = "submission-789"


def _make_submission(state: str, identifier: str = SUBMISSION_ID) -> ReviewSubmission:
    """Build a ReviewSubmission model in the given state.

    :param state: The review submission state value (e.g. "READY_FOR_REVIEW")
    :param identifier: The submission identifier

    :returns: A deserialized ReviewSubmission
    """
    return deserialize.deserialize(
        ReviewSubmission,
        {
            "type": "reviewSubmissions",
            "id": identifier,
            "attributes": {"platform": "IOS", "state": state},
            "relationships": None,
            "links": {"self": f"https://api.example/v1/reviewSubmissions/{identifier}"},
        },
    )


def _make_item(
    version_id: str | None = VERSION_ID, identifier: str = "item-1"
) -> ReviewSubmissionItem:
    """Build a ReviewSubmissionItem model, optionally linked to a version.

    Mirrors what Apple returns for ``GET .../items?include=appStoreVersion``:
    the ``appStoreVersion`` relationship carries a ``data`` linkage when the
    item references a version.

    :param version_id: The app store version the item references, or None for
                       an item that references some other (non-version) resource
    :param identifier: The item identifier

    :returns: A deserialized ReviewSubmissionItem
    """
    relationships: dict | None = None
    if version_id is not None:
        relationships = {
            "appStoreVersion": {
                "data": {"type": "appStoreVersions", "id": version_id},
                "links": {
                    "related": f"https://api.example/v1/reviewSubmissionItems/{identifier}/appStoreVersion"
                },
            }
        }

    return deserialize.deserialize(
        ReviewSubmissionItem,
        {
            "type": "reviewSubmissionItems",
            "id": identifier,
            "relationships": relationships,
            "links": {
                "self": f"https://api.example/v1/reviewSubmissionItems/{identifier}"
            },
        },
    )


def _server_error(status_code: int) -> AppStoreConnectError:
    """Build an AppStoreConnectError carrying the given HTTP status.

    :param status_code: The HTTP status code the error should report

    :returns: An AppStoreConnectError wrapping a mocked response
    """
    response = mock.MagicMock()
    response.status_code = status_code
    response.json.return_value = {
        "errors": [{"status": str(status_code), "code": "X", "title": "Y"}]
    }
    return AppStoreConnectError(response)


def _make_version_client(
    *,
    open_submissions: list,
    items: list,
    created_submission: ReviewSubmission | None,
    submitted_submission: ReviewSubmission | None = None,
) -> tuple[VersionClient, mock.MagicMock]:
    """Build a VersionClient backed by a mocked HTTP client.

    The mock routes GETs by URL shape: ``.../items`` -> the submission's items,
    and the filtered ``.../reviewSubmissions?filter...`` collection -> the
    open-submission lookup. The submit PATCH returns ``submitted_submission`` so
    its (post-submit) state flows back to the caller, mirroring Apple's
    read-your-write PATCH response.

    :param open_submissions: Submissions returned for the open-submission lookup
    :param items: Items returned for the submission-items GET
    :param created_submission: Submission returned by the create POST (or None)
    :param submitted_submission: Submission returned by the submit PATCH;
                                 defaults to a WAITING_FOR_REVIEW one

    :returns: A tuple of the client and its mocked http_client
    """
    http_client = mock.MagicMock()
    http_client.generate_url.side_effect = (
        lambda endpoint: f"https://api.example/v1/{endpoint}"
    )

    def get_side_effect(*, url: str, **_kwargs):  # type: ignore[no-untyped-def]
        """Return mocked GET results based on the requested URL.

        :raises AssertionError: If the URL is not one the test expects

        :returns: An iterator over the configured submissions or items
        :rtype: Iterator
        """
        if "/items" in url:
            return iter(items)
        if "reviewSubmissions" in url:
            return iter(open_submissions)
        raise AssertionError(f"Unexpected GET url: {url}")

    http_client.get.side_effect = get_side_effect
    http_client.post.return_value = created_submission
    http_client.patch.return_value = submitted_submission or _make_submission(
        "WAITING_FOR_REVIEW"
    )

    client = VersionClient(http_client=http_client, log=logging.getLogger("test"))
    return client, http_client


def _post_endpoints(http_client: mock.MagicMock) -> list:
    """Collect the ``endpoint`` of every POST made through the http client.

    :param http_client: The mocked http client

    :returns: The list of endpoints posted to (None for url-based posts)
    """
    return [call.kwargs.get("endpoint") for call in http_client.post.call_args_list]


def _mutation_order(http_client: mock.MagicMock) -> list:
    """Return the ordered sequence of mutating calls (POSTs and PATCHes).

    :param http_client: The mocked http client

    :returns: A list of (verb, endpoint) tuples in call order
    """
    sequence = []
    for name, _args, kwargs in http_client.method_calls:
        if name in ("post", "patch"):
            sequence.append((name, kwargs.get("endpoint")))
    return sequence


def test_submit_creates_submission_when_none_exists() -> None:
    """A fresh submit should create, add the version, then mark submitted."""
    client, http_client = _make_version_client(
        open_submissions=[],
        items=[],
        created_submission=_make_submission("READY_FOR_REVIEW"),
    )

    result = client.submit_for_review(
        app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
    )

    # Both the create and the item-add are POSTs; assert the create happened.
    assert "reviewSubmissions" in _post_endpoints(http_client)

    # The version was attached as an item.
    item_post = next(
        call
        for call in http_client.post.call_args_list
        if call.kwargs.get("endpoint") == "reviewSubmissionItems"
    )
    relationships = item_post.kwargs["data"]["data"]["relationships"]
    assert relationships["reviewSubmission"]["data"]["id"] == SUBMISSION_ID
    assert relationships["appStoreVersion"]["data"]["id"] == VERSION_ID

    # The submission was actually submitted (the step that was previously missing).
    http_client.patch.assert_called_once()
    patch_data = http_client.patch.call_args.kwargs["data"]["data"]
    assert patch_data["id"] == SUBMISSION_ID
    assert patch_data["attributes"]["submitted"] is True

    # The re-read submission (now WAITING_FOR_REVIEW) is returned to the caller.
    assert result.attributes.state == ReviewSubmissionState.WAITING_FOR_REVIEW


def test_submit_adds_item_before_marking_submitted() -> None:
    """The version must be attached before the submit PATCH, or Apple rejects it."""
    client, http_client = _make_version_client(
        open_submissions=[],
        items=[],
        created_submission=_make_submission("READY_FOR_REVIEW"),
    )

    client.submit_for_review(
        app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
    )

    order = _mutation_order(http_client)
    item_index = order.index(("post", "reviewSubmissionItems"))
    patch_index = next(i for i, (verb, _) in enumerate(order) if verb == "patch")
    assert item_index < patch_index, f"item-add must precede submit PATCH: {order}"


def test_lookup_filter_completing_not_complete() -> None:
    """The open-submission lookup must query COMPLETING but never COMPLETE."""
    client, http_client = _make_version_client(
        open_submissions=[],
        items=[],
        created_submission=_make_submission("READY_FOR_REVIEW"),
    )

    client.submit_for_review(
        app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
    )

    filtered_urls = [
        call.kwargs["url"]
        for call in http_client.get.call_args_list
        if "filter" in call.kwargs.get("url", "")
    ]
    assert filtered_urls, "expected a filtered open-submission lookup GET"
    url = filtered_urls[0]
    # COMPLETING must be queried (an in-flight finalising submission is "open").
    assert "COMPLETING" in url
    # COMPLETE must be excluded. ("COMPLETE" is not a substring of "COMPLETING".)
    assert "COMPLETE" not in url
    # The lookup must be scoped to this app and platform - dropping filter[app]
    # would 400 or (worse) surface another app's submission.
    assert "filter[app]=app-123" in url
    assert "filter[platform]=IOS" in url


def test_items_lookup_requests_version_linkage() -> None:
    """The items GET must request include=appStoreVersion for the linkage.

    Without it Apple omits the ``data`` pointer and _item_version_id can no
    longer tell which version an item references - the very check that prevents
    submitting the wrong content. The mock ignores the query string, so only an
    explicit assertion guards against the include being dropped.
    """
    client, http_client = _make_version_client(
        open_submissions=[_make_submission("READY_FOR_REVIEW")],
        items=[],
        created_submission=None,
    )

    client.submit_for_review(
        app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
    )

    item_urls = [
        call.kwargs.get("url", "")
        for call in http_client.get.call_args_list
        if "/items" in call.kwargs.get("url", "")
    ]
    assert item_urls, "expected an items lookup GET"
    assert "include=appStoreVersion" in item_urls[0]


def test_submit_reuses_ready_draft() -> None:
    """An existing READY_FOR_REVIEW draft should be reused, not recreated."""
    client, http_client = _make_version_client(
        open_submissions=[_make_submission("READY_FOR_REVIEW")],
        items=[],
        created_submission=None,
    )

    client.submit_for_review(
        app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
    )

    # No create POST - only the item-add POST should have happened.
    assert _post_endpoints(http_client) == ["reviewSubmissionItems"]
    http_client.patch.assert_called_once()


def test_submit_skips_add_when_same_version_present() -> None:
    """A reused draft that already holds THIS version must not re-add it."""
    client, http_client = _make_version_client(
        open_submissions=[_make_submission("READY_FOR_REVIEW")],
        items=[_make_item(version_id=VERSION_ID)],
        created_submission=None,
    )

    result = client.submit_for_review(
        app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
    )

    # No POSTs at all (no create, no duplicate item), but still submitted.
    assert http_client.post.call_count == 0
    http_client.patch.assert_called_once()
    assert result.attributes.state == ReviewSubmissionState.WAITING_FOR_REVIEW


def test_submit_raises_on_other_version_draft() -> None:
    """A reused draft holding a DIFFERENT version must not be silently submitted."""
    client, http_client = _make_version_client(
        open_submissions=[_make_submission("READY_FOR_REVIEW")],
        items=[_make_item(version_id="some-other-version")],
        created_submission=None,
    )

    with pytest.raises(ValueError, match="do not all match version"):
        client.submit_for_review(
            app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
        )

    # The wrong submission must NOT have been submitted.
    http_client.patch.assert_not_called()
    assert http_client.post.call_count == 0


def test_submit_raises_on_non_version_item() -> None:
    """A reused draft holding a non-version item is also a refuse-to-submit case."""
    client, http_client = _make_version_client(
        open_submissions=[_make_submission("READY_FOR_REVIEW")],
        items=[_make_item(version_id=None)],
        created_submission=None,
    )

    with pytest.raises(ValueError, match="do not all match version"):
        client.submit_for_review(
            app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
        )

    http_client.patch.assert_not_called()


def test_submit_raises_on_mixed_version_draft() -> None:
    """A draft holding our version AND a foreign one must not be submitted.

    Regression for the ``any`` short-circuit: our version being present is not
    enough; if other content rides along it would be submitted too, so every
    item must resolve to our version or the submit is refused.
    """
    client, http_client = _make_version_client(
        open_submissions=[_make_submission("READY_FOR_REVIEW")],
        items=[
            _make_item(version_id=VERSION_ID, identifier="ours"),
            _make_item(version_id="some-other-version", identifier="foreign"),
        ],
        created_submission=None,
    )

    with pytest.raises(ValueError, match="do not all match version"):
        client.submit_for_review(
            app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
        )

    http_client.patch.assert_not_called()


@pytest.mark.parametrize(
    "state",
    ["WAITING_FOR_REVIEW", "IN_REVIEW", "UNRESOLVED_ISSUES", "CANCELING", "COMPLETING"],
)
def test_submit_is_noop_when_already_in_progress(state: str) -> None:
    """If THIS version's submission is already in flight, do nothing and succeed.

    The in-flight submission must contain the requested version - that is what
    makes a re-run an idempotent no-op rather than a different version blocking
    the slot (see test_submit_raises_when_other_version_in_flight).

    This also exercises that a COMPLETING submission deserializes cleanly (the
    missing-enum crash) and is treated as a no-op rather than triggering a
    duplicate create.
    """
    client, http_client = _make_version_client(
        open_submissions=[_make_submission(state)],
        items=[_make_item(version_id=VERSION_ID)],
        created_submission=None,
    )

    result = client.submit_for_review(
        app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
    )

    http_client.post.assert_not_called()
    http_client.patch.assert_not_called()
    assert result.attributes.state.value == state


@pytest.mark.parametrize(
    "state",
    ["WAITING_FOR_REVIEW", "IN_REVIEW", "UNRESOLVED_ISSUES", "CANCELING", "COMPLETING"],
)
def test_submit_raises_when_other_version_in_flight(state: str) -> None:
    """A different version occupying the single open slot must not be a no-op.

    Apple allows only one open submission per app. If that submission is for a
    *different* version, the requested version was never submitted and cannot be
    until the other clears - reporting success here would be a silent lie, so it
    must raise instead.
    """
    client, http_client = _make_version_client(
        open_submissions=[_make_submission(state)],
        items=[_make_item(version_id="some-other-version")],
        created_submission=None,
    )

    with pytest.raises(ValueError, match="does not contain version"):
        client.submit_for_review(
            app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
        )

    # Nothing was created, attached, or submitted - we refused before mutating.
    http_client.post.assert_not_called()
    http_client.patch.assert_not_called()


def test_submit_returns_state_from_patch_response() -> None:
    """The returned submission reflects the PATCH body, not a separate GET.

    Trusting the read-your-write PATCH response avoids failing a good submit
    when a follow-up GET lags Apple's eventual consistency. The only GETs made
    are the open-submission lookup and the items lookup - never a post-submit
    re-read of the single submission.
    """
    client, http_client = _make_version_client(
        open_submissions=[],
        items=[],
        created_submission=_make_submission("READY_FOR_REVIEW"),
        submitted_submission=_make_submission("WAITING_FOR_REVIEW"),
    )

    result = client.submit_for_review(
        app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
    )

    assert result.attributes.state == ReviewSubmissionState.WAITING_FOR_REVIEW

    # No GET should target a single submission by id (that would be a lagging
    # post-submit re-read); only the filtered collection and the items list.
    get_urls = [call.kwargs.get("url", "") for call in http_client.get.call_args_list]
    assert not any(
        "/reviewSubmissions/" in url and "/items" not in url for url in get_urls
    ), f"unexpected single-submission re-read GET in {get_urls}"


def test_submit_handles_create_conflict_by_reusing() -> None:
    """A 409 on create (concurrent submitter) re-discovers and reuses the winner."""
    winner = _make_submission("READY_FOR_REVIEW")

    http_client = mock.MagicMock()
    http_client.generate_url.side_effect = (
        lambda endpoint: f"https://api.example/v1/{endpoint}"
    )

    lookups = {"count": 0}

    def get_side_effect(*, url: str, **_kwargs):  # type: ignore[no-untyped-def]
        """Find nothing on the first lookup, the racing winner on the second.

        :returns: An iterator over the appropriate mocked rows
        :rtype: Iterator
        """
        if "/items" in url:
            return iter([])
        lookups["count"] += 1
        return iter([] if lookups["count"] == 1 else [winner])

    http_client.get.side_effect = get_side_effect

    def post_side_effect(*, endpoint: str | None = None, **_kwargs):  # type: ignore[no-untyped-def]
        """Make only the create conflict; let the item-add succeed.

        :raises AppStoreConnectError: 409 when creating the submission
        """
        if endpoint == "reviewSubmissions":
            raise _server_error(409)

    http_client.post.side_effect = post_side_effect
    http_client.patch.return_value = _make_submission("WAITING_FOR_REVIEW")

    client = VersionClient(http_client=http_client, log=logging.getLogger("test"))

    result = client.submit_for_review(
        app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
    )

    # Create was attempted (and conflicted); the winner was reused and submitted.
    assert "reviewSubmissions" in _post_endpoints(http_client)
    http_client.patch.assert_called_once()
    assert result.attributes.state == ReviewSubmissionState.WAITING_FOR_REVIEW


def test_submit_reuses_partial_submission_across_retry() -> None:
    """A 5xx after the create must not duplicate work on the retry.

    Models the load-bearing idempotency claim: the first attempt creates the
    submission and attaches the version but the submit PATCH 5xx-fails; the
    retry re-discovers that draft (now holding the version) and only submits.
    """
    created = _make_submission("READY_FOR_REVIEW")

    http_client = mock.MagicMock()
    http_client.generate_url.side_effect = (
        lambda endpoint: f"https://api.example/v1/{endpoint}"
    )

    state = {"submitted_once": False}

    def get_side_effect(*, url: str, **_kwargs):  # type: ignore[no-untyped-def]
        """Reflect the partially-built submission once the first PATCH failed.

        :returns: An iterator over the appropriate mocked rows
        :rtype: Iterator
        """
        if "/items" in url:
            return iter(
                [_make_item(version_id=VERSION_ID)] if state["submitted_once"] else []
            )
        return iter([created] if state["submitted_once"] else [])

    http_client.get.side_effect = get_side_effect
    http_client.post.return_value = created

    def patch_side_effect(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        """5xx the first submit PATCH, then succeed on the retry.

        :returns: The submitted submission on the successful retry
        :rtype: ReviewSubmission
        :raises AppStoreConnectError: 503 on the first call
        """
        if not state["submitted_once"]:
            state["submitted_once"] = True
            raise _server_error(503)
        return _make_submission("WAITING_FOR_REVIEW")

    http_client.patch.side_effect = patch_side_effect

    client = VersionClient(http_client=http_client, log=logging.getLogger("test"))

    with mock.patch("asconnect.version_client.time.sleep") as sleep_mock:
        result = client.submit_for_review(
            app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
        )

    sleep_mock.assert_called_once()
    # Exactly one create and one item-add across BOTH attempts - no duplication.
    endpoints = _post_endpoints(http_client)
    assert endpoints.count("reviewSubmissions") == 1
    assert endpoints.count("reviewSubmissionItems") == 1
    assert result.attributes.state == ReviewSubmissionState.WAITING_FOR_REVIEW


def test_submit_exhausts_retries_on_persistent_5xx() -> None:
    """A persistent 5xx is retried max_attempts times, then raised."""
    client, http_client = _make_version_client(
        open_submissions=[],
        items=[],
        created_submission=_make_submission("READY_FOR_REVIEW"),
    )
    http_client.patch.side_effect = _server_error(503)

    with mock.patch("asconnect.version_client.time.sleep") as sleep_mock:
        with pytest.raises(AppStoreConnectError):
            client.submit_for_review(
                app_id=APP_ID,
                version_id=VERSION_ID,
                platform=Platform.IOS,
                max_attempts=2,
            )

    assert sleep_mock.call_count == 2


def test_submit_max_attempts_zero_raises_immediately() -> None:
    """With no attempts left a 5xx propagates without sleeping."""
    client, http_client = _make_version_client(
        open_submissions=[],
        items=[],
        created_submission=_make_submission("READY_FOR_REVIEW"),
    )
    http_client.patch.side_effect = _server_error(503)

    with mock.patch("asconnect.version_client.time.sleep") as sleep_mock:
        with pytest.raises(AppStoreConnectError):
            client.submit_for_review(
                app_id=APP_ID,
                version_id=VERSION_ID,
                platform=Platform.IOS,
                max_attempts=0,
            )

    sleep_mock.assert_not_called()


def test_submit_reraises_non_retriable_error() -> None:
    """A 4xx error should propagate rather than being retried."""
    client, http_client = _make_version_client(
        open_submissions=[],
        items=[],
        created_submission=_make_submission("READY_FOR_REVIEW"),
    )
    http_client.get.side_effect = _server_error(409)

    with pytest.raises(AppStoreConnectError):
        client.submit_for_review(
            app_id=APP_ID, version_id=VERSION_ID, platform=Platform.IOS
        )


def test_completing_state_deserializes() -> None:
    """Regression: Apple's COMPLETING state must not crash deserialization."""
    submission = _make_submission("COMPLETING")
    assert submission.attributes.state == ReviewSubmissionState.COMPLETING
