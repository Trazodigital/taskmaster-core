"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
@sdoc[REQ-FUNC-003]
@sdoc[REQ-FUNC-004]
"""

import json
import logging

from storage.in_memory_repository import InMemoryRepository
from ui.state import TaskmasterState


def test_add_task_appends_and_saves_through_the_repository():
    """@sdoc[REQ-FUNC-001]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)

    state.add_task("buy bread")

    assert [t.text for t in state.tasks] == ["buy bread"]
    assert repo.load().tasks[0].text == "buy bread"


def test_add_task_reports_external_change_and_keeps_the_task_visible():
    """@sdoc[REQ-FUNC-001]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    # someone else writes to the store after this state's last load
    repo.save([], fingerprint=None)

    outcome = state.add_task("buy bread")

    assert outcome.external_change is True
    assert [t.text for t in state.tasks] == ["buy bread"]


def test_add_task_emits_start_and_end_log_events(caplog):
    """@sdoc[REQ-FUNC-001]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)

    with caplog.at_level(logging.INFO, logger="ui.state"):
        state.add_task("buy bread")

    events = [json.loads(r.message) for r in caplog.records]
    assert [e["event_type"] for e in events] == ["start", "end"]
    for e in events:
        assert e["feature"] == "ui"
        assert e["req_uid"] == "REQ-FUNC-001"
        assert e["message"]
    assert events[0]["correlation_id"] == events[1]["correlation_id"]


def test_add_task_emits_error_event_on_external_change(caplog):
    """@sdoc[REQ-FUNC-001]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    repo.save([], fingerprint=None)

    with caplog.at_level(logging.INFO, logger="ui.state"):
        state.add_task("buy bread")

    events = [json.loads(r.message) for r in caplog.records]
    assert [e["event_type"] for e in events] == ["start", "error"]


def test_toggle_task_flips_done_and_saves_through_the_repository():
    """@sdoc[REQ-FUNC-002]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("buy bread")

    state.toggle_task(0)

    assert state.tasks[0].done is True
    assert repo.load().tasks[0].done is True


def test_toggle_task_reports_external_change_and_keeps_the_flip_visible():
    """@sdoc[REQ-FUNC-002]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("buy bread")
    # someone else re-saves the store after this state's last load, bumping
    # the fingerprint state still holds a stale copy of
    current = repo.load()
    repo.save(current.tasks, fingerprint=current.fingerprint)

    outcome = state.toggle_task(0)

    assert outcome.external_change is True
    assert state.tasks[0].done is True


def test_toggle_task_emits_start_and_end_log_events(caplog):
    """@sdoc[REQ-FUNC-002]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("buy bread")
    caplog.clear()  # drop the add_task events from setup above

    with caplog.at_level(logging.INFO, logger="ui.state"):
        state.toggle_task(0)

    events = [json.loads(r.message) for r in caplog.records]
    assert [e["event_type"] for e in events] == ["start", "end"]
    for e in events:
        assert e["req_uid"] == "REQ-FUNC-002"


def test_delete_task_removes_and_saves_through_the_repository():
    """@sdoc[REQ-FUNC-003]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("buy bread")
    state.add_task("walk the dog")

    state.delete_task(0)

    assert [t.text for t in state.tasks] == ["walk the dog"]
    assert [t.text for t in repo.load().tasks] == ["walk the dog"]


def test_delete_task_reports_external_change_and_keeps_the_removal_visible():
    """@sdoc[REQ-FUNC-003]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("buy bread")
    # someone else re-saves the store after this state's last load, bumping
    # the fingerprint state still holds a stale copy of
    current = repo.load()
    repo.save(current.tasks, fingerprint=current.fingerprint)

    outcome = state.delete_task(0)

    assert outcome.external_change is True
    assert state.tasks == []


def test_delete_task_emits_start_and_end_log_events(caplog):
    """@sdoc[REQ-FUNC-003]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("buy bread")
    caplog.clear()  # drop the add_task events from setup above

    with caplog.at_level(logging.INFO, logger="ui.state"):
        state.delete_task(0)

    events = [json.loads(r.message) for r in caplog.records]
    assert [e["event_type"] for e in events] == ["start", "end"]
    for e in events:
        assert e["req_uid"] == "REQ-FUNC-003"


def test_visible_tasks_shows_everything_with_no_active_filter():
    """@sdoc[REQ-FUNC-004]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("buy bread @home")
    state.add_task("ship the release @work")

    assert [t.text for t in state.visible_tasks] == ["buy bread", "ship the release"]


def test_cycle_filter_advances_through_distinct_spaces_then_wraps_to_all():
    """@sdoc[REQ-FUNC-004]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("buy bread @home")
    state.add_task("ship the release @work")

    state.cycle_filter()
    assert state.active_space == "home"
    assert [t.text for t in state.visible_tasks] == ["buy bread"]

    state.cycle_filter()
    assert state.active_space == "work"
    assert [t.text for t in state.visible_tasks] == ["ship the release"]

    state.cycle_filter()
    assert state.active_space is None
    assert [t.text for t in state.visible_tasks] == ["buy bread", "ship the release"]


def test_toggle_task_with_an_active_filter_toggles_the_right_task():
    """@sdoc[REQ-FUNC-004]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("buy bread @home")
    state.add_task("ship the release @work")
    state.cycle_filter()  # active_space = "home"
    state.cycle_filter()  # active_space = "work", visible_tasks = ["ship the release"]

    # index 0 in the FILTERED view is self.tasks[1] in the full list — must
    # resolve there, not to whatever naively sits at self.tasks[0]
    state.toggle_task(0)

    assert [t.done for t in state.tasks] == [False, True]


def test_delete_task_with_an_active_filter_deletes_the_right_task():
    """@sdoc[REQ-FUNC-004]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("buy bread @home")
    state.add_task("ship the release @work")
    state.cycle_filter()  # active_space = "home"
    state.cycle_filter()  # active_space = "work", visible_tasks = ["ship the release"]

    state.delete_task(0)

    assert [t.text for t in state.tasks] == ["buy bread"]


def test_cycle_filter_with_no_spaces_stays_on_all():
    """@sdoc[REQ-FUNC-004]"""
    repo = InMemoryRepository()
    state = TaskmasterState(repo)
    state.add_task("water the plants")

    state.cycle_filter()

    assert state.active_space is None
