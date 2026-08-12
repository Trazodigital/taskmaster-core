"""The composition root is the only site that constructs an adapter.

@sdoc[REQ-FUNC-007]
"""

import logging
from pathlib import Path

import pytest

from src.app import main as app


SOURCE_ROOT = Path(__file__).resolve().parents[2]
REAL_ADAPTERS = ("JsonFileTaskRepository(", "ArgparseCommandInput(")


def _events(caplog, feature):
    """The structured events one module emitted during the call."""
    records = [r for r in caplog.records if hasattr(r, "event_type")]

    return [r for r in records if r.feature == feature]


def test_app_constructs_the_json_repository_with_the_configured_store_path(
    tmp_path, monkeypatch
):
    """The store path reaches the adapter through the composition root.

    @sdoc[REQ-FUNC-007]
    """
    store = tmp_path / "tasks.json"
    constructed = []

    class SpyRepository:
        def __init__(self, store_path, correlation_id):
            constructed.append((store_path, correlation_id))

        def load(self):
            return []

    monkeypatch.setattr(app, "JsonFileTaskRepository", SpyRepository)

    app.main(["list"], env={"TASKMASTER_STORE_PATH": str(store)})

    assert len(constructed) == 1
    store_path, correlation_id = constructed[0]
    assert Path(store_path) == store
    assert correlation_id


@pytest.mark.parametrize("module", ["cli", "tasks", "storage"])
def test_no_module_outside_the_composition_root_constructs_an_adapter(module):
    """Substitutability is a property of the code, not of a convention.

    @sdoc[REQ-FUNC-007]
    """
    offenders = [
        source
        for source in (SOURCE_ROOT / module).rglob("*.py")
        if "tests" not in source.parts
        and any(adapter in source.read_text() for adapter in REAL_ADAPTERS)
    ]

    assert offenders == []


def test_startup_emits_start_then_end_and_no_error(tmp_path, caplog):
    """The run itself is observable, and attributed to this REQ.

    @sdoc[REQ-FUNC-007]
    """
    with caplog.at_level(logging.INFO):
        app.main(
            ["list"],
            env={"TASKMASTER_STORE_PATH": str(tmp_path / "tasks.json")},
        )

    events = _events(caplog, "app")

    assert [r.event_type for r in events] == ["start", "end"]

    for record in events:
        assert record.req_uid == "REQ-FUNC-007"
        assert record.correlation_id


def test_an_unreadable_store_exits_non_zero_and_emits_an_error_event(
    tmp_path, capsys, caplog
):
    """A run against a corrupt store fails explicitly instead of pretending.

    @sdoc[REQ-FUNC-007]
    """
    store = tmp_path / "tasks.json"
    store.write_text('[{"id": "1", "title": "buy mil')
    environment = {"TASKMASTER_STORE_PATH": str(store)}

    with caplog.at_level(logging.INFO):
        exit_code = app.main(["list"], env=environment)

    events = _events(caplog, "app")

    assert exit_code != 0
    assert [r.event_type for r in events] == ["start", "error"]
    assert "Created task" not in capsys.readouterr().out


def test_a_blank_store_path_is_rejected_at_startup(monkeypatch):
    """Config is validated before anything touches the disk.

    @sdoc[REQ-FUNC-007]
    """
    with pytest.raises(app.ConfigError):
        app.main(["list"], env={"TASKMASTER_STORE_PATH": "   "})
