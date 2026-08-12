"""Listing the Tasks a previous run stored.

@sdoc[REQ-FUNC-007]
"""

import logging

import pytest

from src.storage.errors import StorageError
from src.storage.in_memory import InMemoryTaskRepository
from src.tasks.list_tasks import ListingFailed, list_tasks


def _events(caplog, feature):
    """The structured events one module emitted during the call."""
    records = [r for r in caplog.records if hasattr(r, "event_type")]

    return [r for r in records if r.feature == feature]


def test_stored_tasks_are_returned_oldest_first():
    """The Task List is what the repository holds, in the order it holds it.

    @sdoc[REQ-FUNC-007]
    """
    repository = InMemoryTaskRepository()
    first = repository.persist("buy milk")
    second = repository.persist("walk the dog")

    tasks = list_tasks(repository, correlation_id="corr-1")

    assert [(t.id, t.title) for t in tasks] == [
        (first, "buy milk"),
        (second, "walk the dog"),
    ]


def test_an_empty_store_yields_an_empty_task_list_and_no_failure():
    """An empty store is a normal state, never an error.

    @sdoc[REQ-FUNC-007]
    """
    assert list_tasks(InMemoryTaskRepository(), correlation_id="corr-1") == []


def test_a_storage_error_becomes_an_explicit_listing_failure():
    """`cli` sees a failure it can render, not a storage exception.

    @sdoc[REQ-FUNC-007]
    """

    class UnreadableRepository:
        def load(self):
            raise StorageError("stored content is not valid json")

    with pytest.raises(ListingFailed):
        list_tasks(UnreadableRepository(), correlation_id="corr-1")


def test_listing_emits_start_then_end_and_no_error(caplog):
    """A successful listing is observable and attributed to this REQ.

    @sdoc[REQ-FUNC-007]
    """
    with caplog.at_level(logging.INFO):
        list_tasks(InMemoryTaskRepository(), correlation_id="corr-1")

    events = _events(caplog, "tasks")

    assert [r.event_type for r in events] == ["start", "end"]

    for record in events:
        assert record.req_uid == "REQ-FUNC-007"
        assert record.correlation_id == "corr-1"


def test_a_failed_listing_emits_an_error_event(caplog):
    """The failure branch is observable too.

    @sdoc[REQ-FUNC-007]
    """

    class UnreadableRepository:
        def load(self):
            raise StorageError("stored content is not valid json")

    with caplog.at_level(logging.INFO):
        with pytest.raises(ListingFailed):
            list_tasks(UnreadableRepository(), correlation_id="corr-1")

    events = _events(caplog, "tasks")

    assert [r.event_type for r in events] == ["start", "error"]
    assert events[-1].req_uid == "REQ-FUNC-007"
    assert events[-1].correlation_id == "corr-1"
