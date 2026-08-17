"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
@sdoc[REQ-ARCH-001]
@sdoc[REQ-ARCH-006]
@sdoc[REQ-ARCH-008]
@sdoc[REQ-ARCH-009]
"""

import logging
import uuid
from dataclasses import dataclass

from tasks.model import Task, new_task, toggle_done
from tasks.repository import TaskRepository
from ui.logging_events import emit

logger = logging.getLogger(__name__)


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

    def add_task(self, text: str) -> SaveOutcome:
        """@sdoc[REQ-FUNC-001]"""
        return self._save(
            req_uid="REQ-FUNC-001",
            start_message="add_task started",
            end_message="add_task completed",
            mutate=lambda: self.tasks.append(new_task(text)),
        )

    def toggle_task(self, index: int) -> SaveOutcome:
        """@sdoc[REQ-FUNC-002]"""

        def mutate() -> None:
            self.tasks[index] = toggle_done(self.tasks[index])

        return self._save(
            req_uid="REQ-FUNC-002",
            start_message="toggle_task started",
            end_message="toggle_task completed",
            mutate=mutate,
        )

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
