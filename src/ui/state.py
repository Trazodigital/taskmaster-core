"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
@sdoc[REQ-FUNC-003]
@sdoc[REQ-FUNC-004]
@sdoc[REQ-FUNC-005]
@sdoc[REQ-FUNC-006]
@sdoc[REQ-ARCH-001]
@sdoc[REQ-ARCH-006]
@sdoc[REQ-ARCH-008]
@sdoc[REQ-ARCH-009]
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import date

from tasks.model import (
    Task,
    build_task,
    by_space,
    distinct_spaces,
    due_this_week,
    due_today,
    overdue,
    toggle_done,
)

from tasks.repository import TaskRepository
from ui.logging_events import emit

logger = logging.getLogger(__name__)

_DATE_VIEW_FILTERS = {
    "today": due_today,
    "week": due_this_week,
    "overdue": overdue,
}
_DATE_VIEW_CYCLE = [None, "today", "week", "overdue"]


@dataclass
class SaveOutcome:
    external_change: bool


class TaskmasterState:
    """Holds the full task list and the active filter in memory.

    @sdoc[REQ-ARCH-001]
    """

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository
        load_result = repository.load()
        self.tasks: list[Task] = load_result.tasks
        self._fingerprint = load_result.fingerprint
        self.active_space: str | None = None
        self.active_date_view: str | None = None

    @property
    def visible_tasks(self) -> list[Task]:
        """@sdoc[REQ-FUNC-004]
        @sdoc[REQ-FUNC-005]
        """
        tasks = self.tasks
        if self.active_space is not None:
            tasks = by_space(tasks, self.active_space)
        if self.active_date_view is not None:
            tasks = _DATE_VIEW_FILTERS[self.active_date_view](tasks, date.today())
        return tasks

    def cycle_filter(self) -> None:
        """@sdoc[REQ-FUNC-004]"""
        cycle: list[str | None] = [None, *distinct_spaces(self.tasks)]
        current = cycle.index(self.active_space) if self.active_space in cycle else 0
        self.active_space = cycle[(current + 1) % len(cycle)]

    def cycle_date_view(self) -> None:
        """@sdoc[REQ-FUNC-005]"""
        current = _DATE_VIEW_CYCLE.index(self.active_date_view)
        self.active_date_view = _DATE_VIEW_CYCLE[(current + 1) % len(_DATE_VIEW_CYCLE)]

    def add_task(
        self, text: str, *, space: str = "", due_date: str = ""
    ) -> SaveOutcome:
        """@sdoc[REQ-FUNC-001]
        @sdoc[REQ-FUNC-006]
        """
        return self._save(
            req_uid="REQ-FUNC-001",
            start_message="add_task started",
            end_message="add_task completed",
            mutate=lambda: self.tasks.append(
                build_task(text=text, space=space, due_date=due_date)
            ),
        )

    def toggle_task(self, visible_index: int) -> SaveOutcome:
        """@sdoc[REQ-FUNC-002]

        `visible_index` is a position in `visible_tasks` (REQ-FUNC-004), not
        in the full `tasks` list — a filtered view and the full list can
        disagree on where a task sits, so the caller never resolves this
        itself.
        """

        def mutate() -> None:
            index = self._real_index(visible_index)
            self.tasks[index] = toggle_done(self.tasks[index])

        return self._save(
            req_uid="REQ-FUNC-002",
            start_message="toggle_task started",
            end_message="toggle_task completed",
            mutate=mutate,
        )

    def delete_task(self, visible_index: int) -> SaveOutcome:
        """@sdoc[REQ-FUNC-003]

        `visible_index` is a position in `visible_tasks`; see `toggle_task`.
        """
        return self._save(
            req_uid="REQ-FUNC-003",
            start_message="delete_task started",
            end_message="delete_task completed",
            mutate=lambda: self.tasks.pop(self._real_index(visible_index)),
        )

    def _real_index(self, visible_index: int) -> int:
        """@sdoc[REQ-FUNC-004]

        Translates a position in the filtered `visible_tasks` view back to
        its position in the full `tasks` list, by object identity — two
        tasks can be equal by value (same text/done/space), so `==`-based
        lookup could resolve to the wrong one.
        """
        selected = self.visible_tasks[visible_index]
        return next(i for i, task in enumerate(self.tasks) if task is selected)

    def _save(
        self, *, req_uid: str, start_message: str, end_message: str, mutate
    ) -> SaveOutcome:
        correlation_id = uuid.uuid4().hex

        def log(event_type: str, message: str) -> None:
            emit(
                logger,
                event_type,
                feature="ui",
                req_uid=req_uid,
                correlation_id=correlation_id,
                message=message,
            )

        log("start", start_message)

        mutate()
        result = self._repository.save(self.tasks, self._fingerprint)

        if not result.ok:
            log("error", "save rejected: store changed externally")
            return SaveOutcome(external_change=True)

        self._fingerprint = result.fingerprint
        log("end", end_message)
        return SaveOutcome(external_change=False)
