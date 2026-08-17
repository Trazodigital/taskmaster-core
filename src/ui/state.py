"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-ARCH-001]
@sdoc[REQ-ARCH-006]
@sdoc[REQ-ARCH-008]
@sdoc[REQ-ARCH-009]
"""

import logging
import uuid
from dataclasses import dataclass

from tasks.model import Task, new_task
from tasks.repository import TaskRepository
from ui.logging_events import emit

logger = logging.getLogger(__name__)


@dataclass
class AddTaskOutcome:
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

    def add_task(self, text: str) -> AddTaskOutcome:
        """@sdoc[REQ-FUNC-001]"""
        correlation_id = uuid.uuid4().hex

        def log(event_type: str, message: str) -> None:
            emit(
                logger,
                event_type,
                feature="ui",
                req_uid="REQ-FUNC-001",
                correlation_id=correlation_id,
                message=message,
            )

        log("start", "add_task started")

        self.tasks.append(new_task(text))
        result = self._repository.save(self.tasks, self._fingerprint)

        if not result.ok:
            log("error", "save rejected: store changed externally")
            return AddTaskOutcome(external_change=True)

        self._fingerprint = result.fingerprint
        log("end", "add_task completed")
        return AddTaskOutcome(external_change=False)
