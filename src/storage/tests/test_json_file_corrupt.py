"""A store file that cannot be parsed fails loudly and is never overwritten.

@sdoc[REQ-FUNC-005]
"""

import logging

import pytest

from src.storage.errors import StorageError
from src.storage.json_file import JsonFileTaskRepository


CORRUPT = '[{"id": "1", "title": "buy mil'


def _persist(store):
    """Persist one Task through a repository bound to ``store``."""
    JsonFileTaskRepository(store, correlation_id="corr-1").persist("walk")


def test_unparseable_store_raises_a_storage_error(tmp_path):
    """`tasks` sees one error type, whatever the store did wrong.

    @sdoc[REQ-FUNC-005]
    """
    store = tmp_path / "tasks.json"
    store.write_text(CORRUPT)

    with pytest.raises(StorageError):
        _persist(store)


def test_valid_json_that_is_not_a_task_list_raises_a_storage_error(tmp_path):
    """Parseable is not the same as usable; a mapping is not a Task list.

    @sdoc[REQ-FUNC-005]
    """
    store = tmp_path / "tasks.json"
    store.write_text('{"tasks": []}')

    with pytest.raises(StorageError):
        _persist(store)


def test_a_corrupt_store_is_left_byte_for_byte_unchanged(tmp_path):
    """The only copy of those Tasks is the one on disk; it stays repairable.

    @sdoc[REQ-FUNC-005]
    """
    store = tmp_path / "tasks.json"
    store.write_text(CORRUPT)

    with pytest.raises(StorageError):
        _persist(store)

    assert store.read_text() == CORRUPT
    assert list(tmp_path.iterdir()) == [store]


def test_a_corrupt_store_emits_start_then_error(tmp_path, caplog):
    """The failure is observable, and it is attributed to this REQ.

    @sdoc[REQ-FUNC-005]
    """
    store = tmp_path / "tasks.json"
    store.write_text(CORRUPT)
    repository = JsonFileTaskRepository(store, correlation_id="corr-1")

    with caplog.at_level(logging.INFO):
        with pytest.raises(StorageError):
            repository.persist("walk")

    events = [r for r in caplog.records if hasattr(r, "event_type")]
    emitted = [r.event_type for r in events]

    assert emitted == ["start", "error"]
    assert "end" not in emitted
    assert events[-1].req_uid == "REQ-FUNC-005"
    assert events[-1].correlation_id == "corr-1"
    assert events[-1].feature == "storage"
