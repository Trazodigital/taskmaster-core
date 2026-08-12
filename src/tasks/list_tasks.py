"""Return the Tasks the store holds, through the ``task-repository`` port.

Like the create-task use case, this one never names a concrete adapter: an
empty store and an absent store are the same answer here, and deciding which
is which belongs to the adapter.

Emits the structured runtime events required by
``tech-stack-integrations/observability-platform.yaml``, so this REQ carries no
``@no-runtime-events`` opt-out.

@sdoc[REQ-FUNC-007]
"""

import logging

from src.storage.errors import StorageError
from src.tasks.create_task import Task

_LOGGER = logging.getLogger("taskmaster.tasks")
_FEATURE = "tasks"


class ListingFailed(Exception):
    """The stored Tasks could not be read."""


def list_tasks(repository, correlation_id):
    """Return every stored Task, oldest first.

    Raises ``ListingFailed`` when the store cannot be read, so an unreadable
    store never renders as an empty Task List.

    @sdoc[REQ-FUNC-007]
    """
    _emit("start", correlation_id, "task list requested")

    try:
        stored = repository.load()
    except StorageError as exc:
        _emit("error", correlation_id, "task list failed", level=logging.ERROR)

        raise ListingFailed(str(exc)) from exc

    tasks = [Task(id=task["id"], title=task["title"]) for task in stored]

    _emit("end", correlation_id, "task list returned")

    return tasks


def _emit(event_type, correlation_id, message, level=logging.INFO):
    """Emit one structured runtime event with the required fields."""
    _LOGGER.log(
        level,
        message,
        extra={
            "event_type": event_type,
            "feature": _FEATURE,
            "req_uid": "REQ-FUNC-007",
            "correlation_id": correlation_id,
        },
    )
