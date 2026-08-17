"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-005]
@sdoc[REQ-FUNC-006]
@sdoc[REQ-FUNC-007]
@sdoc[REQ-ARCH-001]
@sdoc[REQ-ARCH-013]
"""

import logging
from datetime import date, timedelta
from pathlib import Path

from textual import events
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Input, ListView, ListItem, Label, Static

from storage.json_repository import JsonFileRepository
from tasks.repository import TaskRepository
from ui.state import TaskmasterState

DEFAULT_STORE_PATH = Path.home() / ".local" / "share" / "taskmaster" / "tasks.json"
DEFAULT_LOG_PATH = Path.home() / ".local" / "share" / "taskmaster" / "taskmaster.log"

WELCOME_BANNER = r"""
.·:''''''''''''''''''''''''''''''''''''''''''''''''''''''':·.
: :  _______  _______  _______  __  __                    : :
: : |_     _||   _   ||     __||  |/  |                   : :
: :   |   |  |       ||__     ||     <                    : :
: :   |___|  |___|___||_______||__|\__|                    : :
: :                                                       : :
: :  _______  _______  _______  _______  _______  ______  : :
: : |   |   ||   _   ||     __||_     _||    ___||   __ \ : :
: : |       ||       ||__     |  |   |  |    ___||      < : :
: : |__|_|__||___|___||_______|  |___|  |_______||___|__| : :
'·:.......................................................:·'
"""

WELCOME_GUIDE = """
  a          add a task
  space      toggle done
  d          delete a task
  f          cycle space filter
  v          cycle date view
  tab        move between the add form's fields
  up / down  step the date field by a day
  ?          show this guide again

  press any key to continue
"""


class DateInput(Input):
    """A single-line date field steppable by day with up/down.

    @sdoc[REQ-FUNC-006]
    """

    BINDINGS = [
        ("up", "step_date(1)", "Later"),
        ("down", "step_date(-1)", "Earlier"),
    ]

    def action_step_date(self, days: int) -> None:
        try:
            current = date.fromisoformat(self.value)
        except ValueError:
            current = date.today()
        self.value = (current + timedelta(days=days)).isoformat()


class WelcomeScreen(Screen):
    """The banner and key-bindings guide shown before the task list.

    @sdoc[REQ-FUNC-007]
    """

    def compose(self) -> ComposeResult:
        yield Static(WELCOME_BANNER, markup=False, id="welcome-banner")
        yield Static(WELCOME_GUIDE, markup=False, id="welcome-guide")

    def on_key(self, event: events.Key) -> None:
        self.app.pop_screen()


class TaskmasterApp(App):
    """The composition root. Wires the real adapter and holds all state.

    @sdoc[REQ-ARCH-001]
    """

    BINDINGS = [
        ("a", "add_task", "Add task"),
        ("space", "toggle_task", "Toggle done"),
        ("d", "delete_task", "Delete task"),
        ("f", "cycle_filter", "Cycle filter"),
        ("v", "cycle_date_view", "Cycle date view"),
        ("?", "show_help", "Show help"),
    ]

    def __init__(
        self,
        repository: TaskRepository | None = None,
        log_path: Path = DEFAULT_LOG_PATH,
    ) -> None:
        super().__init__()
        self._configure_logging(log_path)
        if repository is None:
            DEFAULT_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
            repository = JsonFileRepository(DEFAULT_STORE_PATH)
        self.state = TaskmasterState(repository)

    @staticmethod
    def _configure_logging(log_path: Path) -> None:
        """Logs go to a file, never the terminal — ADR 0006.

        @sdoc[REQ-ARCH-013]
        """
        log_path.parent.mkdir(parents=True, exist_ok=True)
        ui_logger = logging.getLogger("ui")
        ui_logger.setLevel(logging.INFO)
        for handler in list(ui_logger.handlers):
            ui_logger.removeHandler(handler)
        ui_logger.addHandler(logging.FileHandler(log_path))

    def compose(self) -> ComposeResult:
        yield Input(placeholder="add a task", id="task-input")
        yield Input(placeholder="space (optional)", id="space-input")
        yield DateInput(value=date.today().isoformat(), id="date-input")
        yield ListView(id="task-list")

    def on_mount(self) -> None:
        self._refresh_list()
        # the list holds focus, not the input — otherwise every single-key
        # binding below (toggle/delete/cycle-*) is typed into the input as a
        # literal character instead of ever reaching these actions
        self.query_one("#task-list", ListView).focus()
        self.push_screen(WelcomeScreen())

    def action_show_help(self) -> None:
        """@sdoc[REQ-FUNC-007]"""
        self.push_screen(WelcomeScreen())

    def action_add_task(self) -> None:
        """@sdoc[REQ-FUNC-001]

        Only focuses the input; creating the task happens on Submitted
        (Enter), in `on_input_submitted`. Reading the input's value here
        would be moot anyway — while the input holds focus, the single
        letter "a" never reaches this action, it is typed into the input.
        """
        self.query_one("#task-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """@sdoc[REQ-FUNC-001]
        @sdoc[REQ-FUNC-006]

        Fires on Enter from any of the three fields (text/space/date), so it
        always reads all three current values rather than just the field
        that triggered submission.
        """
        text_input = self.query_one("#task-input", Input)
        space_input = self.query_one("#space-input", Input)
        date_input = self.query_one("#date-input", Input)
        text = text_input.value
        if text:
            self.state.add_task(
                text, space=space_input.value, due_date=date_input.value
            )
            text_input.value = ""
            space_input.value = ""
            date_input.value = date.today().isoformat()
            self._refresh_list()
        self.query_one("#task-list", ListView).focus()

    def action_toggle_task(self) -> None:
        """@sdoc[REQ-FUNC-002]"""
        self._act_on_selected(self.state.toggle_task)

    def action_delete_task(self) -> None:
        """@sdoc[REQ-FUNC-003]"""
        self._act_on_selected(self.state.delete_task)

    def action_cycle_filter(self) -> None:
        """@sdoc[REQ-FUNC-004]"""
        self.state.cycle_filter()
        self._refresh_list()

    def action_cycle_date_view(self) -> None:
        """@sdoc[REQ-FUNC-005]"""
        self.state.cycle_date_view()
        self._refresh_list()

    def _act_on_selected(self, action) -> None:
        task_list = self.query_one("#task-list", ListView)
        index = task_list.index
        if index is None:
            return
        action(index)
        self._refresh_list()

    def _refresh_list(self) -> None:
        """@sdoc[REQ-FUNC-001]"""
        task_list = self.query_one("#task-list", ListView)
        task_list.clear()
        for task in self.state.visible_tasks:
            mark = "x" if task.done else " "
            # markup=False: task text is arbitrary user input, never
            # interpreted as Rich markup — REQ-ARCH-018's untrusted-input
            # posture applies here too, not just to the stored JSON.
            task_list.append(ListItem(Label(f"[{mark}] {task.text}", markup=False)))
        # ListView.clear() drops the selection; without re-selecting, toggle
        # and delete are unreachable until the user manually presses an
        # arrow key first — same reachability defect as the focus bug above.
        if task_list.index is None and len(task_list) > 0:
            task_list.index = 0
