"""Durable persistence of a Task in a JSON file on disk.

@sdoc[REQ-FUNC-004]
"""

import json
import logging
import os

from src.storage.json_file import JsonFileTaskRepository


def test_absent_store_is_treated_as_empty_and_created_on_persist(tmp_path):
    """A first run has no store file; the persist creates one holding the Task.

    @sdoc[REQ-FUNC-004]
    """
    store = tmp_path / "tasks.json"
    repository = JsonFileTaskRepository(store, correlation_id="corr-1")

    task_id = repository.persist("buy milk")

    stored = json.loads(store.read_text())

    assert stored == [{"id": task_id, "title": "buy milk"}]


def test_persist_appends_and_returns_the_identifier(tmp_path):
    """An existing store is read whole, appended to, and written back whole.

    @sdoc[REQ-FUNC-004]
    """
    store = tmp_path / "tasks.json"
    store.write_text(json.dumps([{"id": "1", "title": "buy milk"}]))
    repository = JsonFileTaskRepository(store, correlation_id="corr-1")

    task_id = repository.persist("walk the dog")

    stored = json.loads(store.read_text())

    assert task_id != "1"
    assert stored == [
        {"id": "1", "title": "buy milk"},
        {"id": task_id, "title": "walk the dog"},
    ]


def test_store_is_promoted_by_an_atomic_replace(tmp_path, monkeypatch):
    """The new document lands via a rename inside the store's own directory.

    A rename across filesystems is not atomic, so the temporary file has to be
    a sibling of the store rather than a file under the system temp directory.

    @sdoc[REQ-FUNC-004]
    """
    store = tmp_path / "tasks.json"
    promotions = []
    real_replace = os.replace

    def recording_replace(source, target):
        promotions.append((source, target))
        real_replace(source, target)

    monkeypatch.setattr(os, "replace", recording_replace)

    JsonFileTaskRepository(store, correlation_id="corr-1").persist("buy milk")

    assert len(promotions) == 1
    source, target = promotions[0]
    assert os.path.dirname(source) == os.path.dirname(target) == str(tmp_path)
    assert list(tmp_path.iterdir()) == [store]


def test_persist_emits_start_then_end_and_no_error(tmp_path, caplog):
    """The adapter reports its own lifecycle, so a write stays traceable.

    @sdoc[REQ-FUNC-004]
    """
    repository = JsonFileTaskRepository(
        tmp_path / "tasks.json", correlation_id="corr-1"
    )

    with caplog.at_level(logging.INFO):
        repository.persist("buy milk")

    events = [r for r in caplog.records if hasattr(r, "event_type")]

    assert [r.event_type for r in events] == ["start", "end"]

    for record in events:
        assert record.req_uid == "REQ-FUNC-004"
        assert record.correlation_id == "corr-1"
        assert record.feature == "storage"
        assert "buy milk" not in record.getMessage()
