"""A failed store write surfaces as an error and destroys nothing.

@sdoc[REQ-FUNC-006]
"""

import json
import logging
import os

import pytest

from src.storage.errors import StorageError
from src.storage.json_file import JsonFileTaskRepository


STORED = [{"id": "1", "title": "buy milk"}]


def _persist(store):
    """Persist one Task through a repository bound to ``store``."""
    JsonFileTaskRepository(store, correlation_id="corr-1").persist("walk")


def _store_with_one_task(tmp_path):
    """A store holding one Task, written the way the adapter would write it."""
    store = tmp_path / "tasks.json"
    store.write_text(json.dumps(STORED))

    return store


def _breaking_replace(monkeypatch):
    """Make the promotion fail the way a full or read-only disk would."""

    def failing_replace(source, target):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(os, "replace", failing_replace)


def test_a_failed_write_raises_a_storage_error_and_returns_no_identifier(
    tmp_path, monkeypatch
):
    """No identifier can be reported for a Task that never reached the disk.

    @sdoc[REQ-FUNC-006]
    """
    store = _store_with_one_task(tmp_path)
    _breaking_replace(monkeypatch)

    with pytest.raises(StorageError):
        _persist(store)


def test_a_failed_write_leaves_the_previously_stored_tasks_intact(
    tmp_path, monkeypatch
):
    """The store still holds exactly what it held before the failed persist.

    @sdoc[REQ-FUNC-006]
    """
    store = _store_with_one_task(tmp_path)
    _breaking_replace(monkeypatch)

    with pytest.raises(StorageError):
        _persist(store)

    assert json.loads(store.read_text()) == STORED


def test_a_failed_write_leaves_no_temporary_document(tmp_path, monkeypatch):
    """The half-written document is dropped rather than left next to the store.

    @sdoc[REQ-FUNC-006]
    """
    store = _store_with_one_task(tmp_path)
    _breaking_replace(monkeypatch)

    with pytest.raises(StorageError):
        _persist(store)

    assert list(tmp_path.iterdir()) == [store]


def test_a_failed_write_emits_start_then_error_and_never_end(
    tmp_path, monkeypatch, caplog
):
    """The failure is observable, and it is attributed to this REQ.

    @sdoc[REQ-FUNC-006]
    """
    store = _store_with_one_task(tmp_path)
    _breaking_replace(monkeypatch)
    repository = JsonFileTaskRepository(store, correlation_id="corr-1")

    with caplog.at_level(logging.INFO):
        with pytest.raises(StorageError):
            repository.persist("walk")

    events = [r for r in caplog.records if hasattr(r, "event_type")]

    assert [r.event_type for r in events] == ["start", "error"]
    assert events[-1].req_uid == "REQ-FUNC-006"
    assert events[-1].correlation_id == "corr-1"
    assert events[-1].feature == "storage"


def test_an_unreadable_store_is_a_storage_error_too(tmp_path, monkeypatch):
    """A read that fails for any reason other than absence is a real failure.

    An absent store means a first run; a store that exists and cannot be read
    means the Tasks are there and unreachable, which must never be silently
    treated as an empty store.

    @sdoc[REQ-FUNC-006]
    """
    store = _store_with_one_task(tmp_path)

    def failing_read(*args, **kwargs):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr("pathlib.Path.read_text", failing_read)

    with pytest.raises(StorageError):
        _persist(store)
