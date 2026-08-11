"""Create-task failure paths: storage errors and the persist timeout.

@sdoc[REQ-FUNC-003]
"""

import logging
import threading

import pytest

from src.cli.command_input import parse_create_task
from src.storage.errors import StorageError
from src.tasks.create_task import (
    PERSIST_TIMEOUT_SECONDS,
    CreationFailed,
    create_task,
)


class FailingRepository:
    """Satisfies task-repository by always failing the write."""

    def __init__(self):
        self.calls = 0

    def persist(self, title):
        self.calls += 1
        raise StorageError("disk unavailable")


class HangingRepository:
    """Satisfies task-repository by never completing the write."""

    def __init__(self):
        self.calls = 0
        self.release = threading.Event()

    def persist(self, title):
        self.calls += 1
        self.release.wait(timeout=30)

        return "never-returned"


def test_storage_error_becomes_a_creation_failure():
    """A failed write is reported, never swallowed.

    @sdoc[REQ-FUNC-003]
    """
    repository = FailingRepository()

    with pytest.raises(CreationFailed):
        create_task(parse_create_task("buy milk"), repository, "corr-1")


def test_timed_out_write_fails_and_is_not_retried():
    """The write is abandoned after the budget and never re-issued.

    @sdoc[REQ-FUNC-003]
    """
    repository = HangingRepository()

    try:
        with pytest.raises(CreationFailed):
            create_task(
                parse_create_task("buy milk"),
                repository,
                "corr-1",
                timeout_seconds=0.05,
            )

        assert repository.calls == 1
    finally:
        repository.release.set()


def test_persist_timeout_matches_the_architecture_budget():
    """The default budget is the 5 seconds REQ-ARCH-022 declares.

    @sdoc[REQ-FUNC-003]
    """
    assert PERSIST_TIMEOUT_SECONDS == 5


def test_failure_emits_start_then_error_and_no_end(caplog):
    """A failed create emits start and error, never end.

    @sdoc[REQ-FUNC-003]
    """
    with caplog.at_level(logging.INFO):
        with pytest.raises(CreationFailed):
            create_task(
                parse_create_task("buy milk"),
                FailingRepository(),
                "corr-9",
            )

    events = [r for r in caplog.records if hasattr(r, "event_type")]
    types = [r.event_type for r in events]

    assert types == ["start", "error"]
    assert "end" not in types

    for record in events:
        assert record.req_uid in ("REQ-FUNC-001", "REQ-FUNC-003")
        assert record.correlation_id == "corr-9"
        assert record.feature == "create-task"
