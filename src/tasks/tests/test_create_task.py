"""Create-task use case: persistence and the events it emits.

@sdoc[REQ-FUNC-001]
"""

import logging

from src.cli.command_input import parse_create_task
from src.storage.in_memory import InMemoryTaskRepository
from src.tasks.create_task import create_task


def test_task_is_persisted_and_its_identifier_returned():
    """storage returns the identifier the Task is created with.

    @sdoc[REQ-FUNC-001]
    """
    repository = InMemoryTaskRepository()

    task = create_task(
        parse_create_task("buy milk"),
        repository,
        correlation_id="corr-1",
    )

    assert task.id
    assert task.title == "buy milk"
    assert repository.stored(task.id) == "buy milk"


def test_happy_path_emits_start_then_end_and_no_error(caplog):
    """A successful create emits start and end, never error.

    @sdoc[REQ-FUNC-001]
    """
    with caplog.at_level(logging.INFO):
        create_task(
            parse_create_task("buy milk"),
            InMemoryTaskRepository(),
            correlation_id="corr-1",
        )

    events = [r for r in caplog.records if hasattr(r, "event_type")]
    types = [r.event_type for r in events]

    assert types == ["start", "end"]
    assert "error" not in types

    for record in events:
        assert record.req_uid == "REQ-FUNC-001"
        assert record.correlation_id == "corr-1"
        assert record.feature == "create-task"
