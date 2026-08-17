"""
@sdoc[REQ-FUNC-001]
"""

from storage.in_memory_repository import InMemoryRepository
from tasks.model import new_task


def test_save_then_load_round_trips_the_task_list():
    """@sdoc[REQ-FUNC-001]"""
    repo = InMemoryRepository()
    tasks = [new_task("buy bread")]

    save_result = repo.save(tasks, fingerprint=None)
    load_result = repo.load()

    assert save_result.ok is True
    assert load_result.tasks == tasks


def test_save_rejects_a_stale_fingerprint():
    """@sdoc[REQ-FUNC-001]"""
    repo = InMemoryRepository()
    repo.save([new_task("first")], fingerprint=None)
    stale_fingerprint = None  # the caller never re-read after the first save

    result = repo.save([new_task("second")], fingerprint=stale_fingerprint)

    assert result.ok is False
