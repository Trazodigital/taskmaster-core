"""Create a Task and persist it through the ``task-repository`` port.

The use case never names a concrete adapter: it receives whatever satisfies
the port, which is what keeps ``app`` the only module that constructs
adapters.

Emits the structured runtime events required by
``tech-stack-integrations/observability-platform.yaml``, so these REQs carry
no ``@no-runtime-events`` opt-out.

@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-003]
"""

import concurrent.futures
import logging
from dataclasses import dataclass

from src.storage.errors import StorageError

_LOGGER = logging.getLogger("taskmaster.tasks")
_FEATURE = "create-task"

#: Write budget declared by REQ-ARCH-022. A write that exceeds it is abandoned
#: and treated as a storage error; it is never retried automatically.
PERSIST_TIMEOUT_SECONDS = 5


class CreationFailed(Exception):
    """A Task could not be created, for any reason below the use case."""


@dataclass(frozen=True)
class Task:
    """A Task the User has created, carrying the identifier storage gave."""

    id: str
    title: str


def _emit(event_type, req_uid, correlation_id, message):
    """Emit one structured runtime event with the required fields."""
    _LOGGER.info(
        message,
        extra={
            "event_type": event_type,
            "feature": _FEATURE,
            "req_uid": req_uid,
            "correlation_id": correlation_id,
        },
    )


def _fail(correlation_id, reason):
    """Report a creation failure and stop. No retry is ever issued."""
    _emit("error", "REQ-FUNC-003", correlation_id, "task creation failed")

    raise CreationFailed(reason)


def create_task(
    command,
    repository,
    correlation_id,
    timeout_seconds=PERSIST_TIMEOUT_SECONDS,
):
    """Persist the command's Task and return it with its identifier.

    Raises ``CreationFailed`` when the write fails or outlives its budget, so
    a failure can never reach the User shaped like a success.

    @sdoc[REQ-FUNC-001]
    @sdoc[REQ-FUNC-003]
    """
    _emit("start", "REQ-FUNC-001", correlation_id, "create task requested")

    # The write runs on a worker so waiting for it can be abandoned: a
    # repository blocked on a disk or a lock would otherwise hold the caller
    # indefinitely. Shutdown is deliberately non-blocking — joining the pool
    # would re-introduce exactly the wait the budget exists to bound.
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        future = pool.submit(repository.persist, command.title)
        task_id = future.result(timeout=timeout_seconds)
    except concurrent.futures.TimeoutError:
        _fail(
            correlation_id,
            f"storage did not respond within {timeout_seconds}s",
        )
    except StorageError as exc:
        _fail(correlation_id, str(exc))
    finally:
        pool.shutdown(wait=False)

    task = Task(id=task_id, title=command.title)

    _emit("end", "REQ-FUNC-001", correlation_id, "task created")

    return task
