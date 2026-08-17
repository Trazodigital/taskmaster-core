"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
@sdoc[REQ-FUNC-003]
@sdoc[REQ-FUNC-004]
@sdoc[REQ-FUNC-005]
"""

import logging

from textual.widgets import Label

from storage.in_memory_repository import InMemoryRepository
from ui.app import TaskmasterApp


def test_app_binds_the_add_key():
    """@sdoc[REQ-FUNC-001]"""
    app = TaskmasterApp(repository=InMemoryRepository())

    bindings = app._bindings.get_bindings_for_key("a")
    assert [b.action for b in bindings] == ["add_task"]


def test_app_binds_the_toggle_key():
    """@sdoc[REQ-FUNC-002]"""
    app = TaskmasterApp(repository=InMemoryRepository())

    bindings = app._bindings.get_bindings_for_key("space")
    assert [b.action for b in bindings] == ["toggle_task"]


def test_app_binds_the_delete_key():
    """@sdoc[REQ-FUNC-003]"""
    app = TaskmasterApp(repository=InMemoryRepository())

    bindings = app._bindings.get_bindings_for_key("d")
    assert [b.action for b in bindings] == ["delete_task"]


def test_app_binds_the_cycle_filter_key():
    """@sdoc[REQ-FUNC-004]"""
    app = TaskmasterApp(repository=InMemoryRepository())

    bindings = app._bindings.get_bindings_for_key("f")
    assert [b.action for b in bindings] == ["cycle_filter"]


def test_app_binds_the_cycle_date_view_key():
    """@sdoc[REQ-FUNC-005]"""
    app = TaskmasterApp(repository=InMemoryRepository())

    bindings = app._bindings.get_bindings_for_key("v")
    assert [b.action for b in bindings] == ["cycle_date_view"]


def test_task_line_renders_bracket_text_literally_not_as_markup():
    """@sdoc[REQ-FUNC-002]"""
    # task text is arbitrary user input; Rich markup parsing would silently
    # eat a literal "[x]" or "[bold]...[/bold]" typed by the user
    line = Label("[x] [bold]urgent[/bold]", markup=False)

    assert str(line.render()) == "[x] [bold]urgent[/bold]"


def test_app_wires_its_state_to_the_injected_repository():
    """@sdoc[REQ-FUNC-001]"""
    repo = InMemoryRepository()
    repo.save([], fingerprint=None)

    app = TaskmasterApp(repository=repo)

    assert app.state.tasks == []


def test_app_logs_to_a_file_and_never_to_the_terminal(tmp_path):
    """@sdoc[REQ-ARCH-013]"""
    log_path = tmp_path / "taskmaster.log"

    TaskmasterApp(repository=InMemoryRepository(), log_path=log_path)

    handlers = logging.getLogger("ui").handlers
    assert any(
        isinstance(h, logging.FileHandler) and h.baseFilename == str(log_path)
        for h in handlers
    )
    non_file_stream_handlers = [
        h
        for h in handlers
        if isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.FileHandler)
    ]
    assert non_file_stream_handlers == []
