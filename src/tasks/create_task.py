"""Create a Task and persist it through the ``task-repository`` port.

The use case never names a concrete adapter: it receives whatever satisfies
the port, which is what keeps ``app`` the only module that constructs
adapters.

Emits the structured runtime events required by
``tech-stack-integrations/observability-platform.yaml``, so this REQ carries
no ``@no-runtime-events`` opt-out.

@sdoc[REQ-FUNC-001]
"""

import logging
from dataclasses import dataclass

_LOGGER = logging.getLogger("taskmaster.tasks")
_FEATURE = "create-task"
_REQ = "REQ-FUNC-001"


@dataclass(frozen=True)
class Task:
    """A Task the User has created, carrying the identifier storage gave."""

    id: str
    title: str


def _emit(event_type, correlation_id, message):
    """Emit one structured runtime event with the required fields."""
    _LOGGER.info(
        message,
        extra={
            "event_type": event_type,
            "feature": _FEATURE,
            "req_uid": _REQ,
            "correlation_id": correlation_id,
        },
    )


def create_task(command, repository, correlation_id):
    """Persist the command's Task and return it with its identifier.

    @sdoc[REQ-FUNC-001]
    """
    _emit("start", correlation_id, "create task requested")

    task_id = repository.persist(command.title)
    task = Task(id=task_id, title=command.title)

    _emit("end", correlation_id, "task created")

    return task
