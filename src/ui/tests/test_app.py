"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
@sdoc[REQ-FUNC-003]
@sdoc[REQ-FUNC-004]
@sdoc[REQ-FUNC-005]
@sdoc[REQ-FUNC-006]
"""

import asyncio
import logging
from datetime import date, timedelta

from textual.widgets import Input, ListView, Label

from storage.in_memory_repository import InMemoryRepository
from ui.app import TaskmasterApp


def run(coro):
    """Drive an async Pilot flow from a plain sync test.

    No pytest-asyncio dependency: this function owns the event loop itself
    rather than asking pytest to run an async test function.

    @sdoc[REQ-FUNC-001]
    """
    return asyncio.run(coro)


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


def test_task_list_holds_focus_on_start_not_the_input():
    """@sdoc[REQ-FUNC-001]"""

    async def scenario():
        app = TaskmasterApp(repository=InMemoryRepository())
        async with app.run_test():
            return app.focused

    focused = run(scenario())
    assert isinstance(focused, ListView)


def test_pressing_a_key_focuses_the_input_without_creating_a_task():
    """@sdoc[REQ-FUNC-001]"""

    async def scenario():
        app = TaskmasterApp(repository=InMemoryRepository())
        async with app.run_test() as pilot:
            await pilot.press("a")
            return app.focused, app.state.tasks

    focused, tasks = run(scenario())
    assert isinstance(focused, Input)
    assert tasks == []


def test_typing_then_enter_creates_the_task_and_returns_focus_to_the_list():
    """@sdoc[REQ-FUNC-001]"""

    async def scenario():
        app = TaskmasterApp(repository=InMemoryRepository())
        async with app.run_test() as pilot:
            await pilot.press("a")
            for ch in "buy bread":
                await pilot.press(ch if ch != " " else "space")
            await pilot.press("enter")
            return app.focused, [t.text for t in app.state.tasks]

    focused, texts = run(scenario())
    assert isinstance(focused, ListView)
    assert texts == ["buy bread"]


def test_adding_a_task_leaves_it_selected_so_toggle_works_immediately():
    """@sdoc[REQ-FUNC-001]"""

    async def scenario():
        app = TaskmasterApp(repository=InMemoryRepository())
        async with app.run_test() as pilot:
            await pilot.press("a")
            for ch in "buy bread":
                await pilot.press(ch if ch != " " else "space")
            await pilot.press("enter")
            await pilot.press("space")  # toggle, with no manual selection
            return app.state.tasks[0].done

    assert run(scenario()) is True


def test_toggle_key_reaches_the_app_while_the_list_holds_focus():
    """@sdoc[REQ-FUNC-002]"""

    async def scenario():
        app = TaskmasterApp(repository=InMemoryRepository())
        app.state.add_task("buy bread")
        async with app.run_test() as pilot:
            app.query_one(ListView).index = 0
            await pilot.press("space")
            return app.state.tasks[0].done

    assert run(scenario()) is True


def test_date_field_is_prefilled_with_todays_date():
    """@sdoc[REQ-FUNC-006]"""

    async def scenario():
        app = TaskmasterApp(repository=InMemoryRepository())
        async with app.run_test():
            return app.query_one("#date-input", Input).value

    assert run(scenario()) == date.today().isoformat()


def test_up_on_the_date_field_advances_it_by_one_day():
    """@sdoc[REQ-FUNC-006]"""

    async def scenario():
        app = TaskmasterApp(repository=InMemoryRepository())
        async with app.run_test() as pilot:
            app.query_one("#date-input", Input).focus()
            await pilot.press("up")
            return app.query_one("#date-input", Input).value

    expected = (date.today() + timedelta(days=1)).isoformat()
    assert run(scenario()) == expected


def test_down_on_the_date_field_retreats_it_by_one_day():
    """@sdoc[REQ-FUNC-006]"""

    async def scenario():
        app = TaskmasterApp(repository=InMemoryRepository())
        async with app.run_test() as pilot:
            app.query_one("#date-input", Input).focus()
            await pilot.press("down")
            return app.query_one("#date-input", Input).value

    expected = (date.today() - timedelta(days=1)).isoformat()
    assert run(scenario()) == expected


def test_submitting_the_form_creates_a_task_with_the_space_and_date_fields():
    """@sdoc[REQ-FUNC-006]"""

    async def scenario():
        app = TaskmasterApp(repository=InMemoryRepository())
        async with app.run_test() as pilot:
            app.query_one("#task-input", Input).value = "buy bread"
            app.query_one("#space-input", Input).value = "home"
            app.query_one("#date-input", Input).value = "2026-08-20"
            app.query_one("#task-input", Input).focus()
            await pilot.press("enter")
            return app.state.tasks[0]

    task = run(scenario())
    assert task.text == "buy bread"
    assert task.space == "home"
    assert task.due_date == date(2026, 8, 20)


def test_submitting_the_form_clears_text_and_space_and_resets_the_date_to_today():
    """@sdoc[REQ-FUNC-006]"""

    async def scenario():
        app = TaskmasterApp(repository=InMemoryRepository())
        async with app.run_test() as pilot:
            app.query_one("#task-input", Input).value = "buy bread"
            app.query_one("#space-input", Input).value = "home"
            app.query_one("#date-input", Input).value = "2026-08-20"
            app.query_one("#task-input", Input).focus()
            await pilot.press("enter")
            return (
                app.query_one("#task-input", Input).value,
                app.query_one("#space-input", Input).value,
                app.query_one("#date-input", Input).value,
            )

    text_value, space_value, date_value = run(scenario())
    assert text_value == ""
    assert space_value == ""
    assert date_value == date.today().isoformat()


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
