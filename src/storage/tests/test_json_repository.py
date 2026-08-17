"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-ARCH-017]
@sdoc[REQ-ARCH-018]
@sdoc[REQ-ARCH-019]
@sdoc[REQ-ARCH-020]
@sdoc[REQ-ARCH-021]
"""

from storage.json_repository import JsonFileRepository
from tasks.model import new_task


def test_load_on_a_missing_store_yields_an_empty_list(tmp_path):
    """@sdoc[REQ-ARCH-017]"""
    repo = JsonFileRepository(tmp_path / "tasks.json")

    result = repo.load()

    assert result.tasks == []
    assert result.fingerprint is None
    assert result.error is None


def test_save_then_load_round_trips_through_a_new_instance(tmp_path):
    """@sdoc[REQ-FUNC-001]"""
    store = tmp_path / "tasks.json"
    writer = JsonFileRepository(store)
    save_result = writer.save([new_task("buy bread")], fingerprint=None)

    reader = JsonFileRepository(store)
    load_result = reader.load()

    assert save_result.ok is True
    assert [t.text for t in load_result.tasks] == ["buy bread"]
    assert load_result.fingerprint == save_result.fingerprint


def test_save_leaves_no_temporary_file_behind(tmp_path):
    """@sdoc[REQ-ARCH-021]"""
    store = tmp_path / "tasks.json"
    repo = JsonFileRepository(store)

    repo.save([new_task("buy bread")], fingerprint=None)

    assert store.exists()
    assert list(tmp_path.glob("*.tmp")) == []


def test_load_on_unparseable_content_reports_an_error_and_yields_no_tasks(tmp_path):
    """@sdoc[REQ-ARCH-018]"""
    store = tmp_path / "tasks.json"
    store.write_text("{not valid json", encoding="utf-8")
    repo = JsonFileRepository(store)

    result = repo.load()

    assert result.error is not None
    assert result.tasks == []


def test_save_with_a_stale_fingerprint_writes_nothing(tmp_path):
    """@sdoc[REQ-ARCH-019]
    @sdoc[REQ-ARCH-020]
    """
    store = tmp_path / "tasks.json"
    repo = JsonFileRepository(store)
    repo.save([new_task("first")], fingerprint=None)
    before = store.read_bytes()

    result = repo.save([new_task("second")], fingerprint=None)

    assert result.ok is False
    assert store.read_bytes() == before
