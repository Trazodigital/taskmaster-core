"""Composition root and process entrypoint.

The only module that constructs a concrete adapter: it resolves the store
path, builds the file-backed task-repository, and hands it to the use cases.
That is what keeps every other module testable against a double.

Emits the structured runtime events required by
``tech-stack-integrations/observability-platform.yaml``, so this REQ carries no
``@no-runtime-events`` opt-out.

@sdoc[REQ-FUNC-007]
@adr[0004]
"""

import logging
import os
import sys
import uuid

from src.app.config import ConfigError, store_path
from src.cli.command_input import (
    CreateTaskCommand,
    InvalidCommand,
    parse_command,
)
from src.cli.presenter import (
    render_created,
    render_failed,
    render_listing_failed,
    render_task_list,
)
from src.storage.json_file import JsonFileTaskRepository
from src.tasks.create_task import CreationFailed, create_task
from src.tasks.list_tasks import ListingFailed, list_tasks

_LOGGER = logging.getLogger("taskmaster.app")
_FEATURE = "app"

#: ``ConfigError`` is re-exported: a caller that starts the process should
#: not have to know which module reads the environment.
__all__ = ["main", "ConfigError"]

FAILURE_EXIT_CODE = 1


def main(argv=None, env=None):
    """Run one Command against the configured store and return an exit code.

    Raises ``ConfigError`` before any work when the configuration is unusable;
    every other failure is rendered to the User and reported as a non-zero
    exit code.

    @sdoc[REQ-FUNC-007]
    """
    arguments = sys.argv[1:] if argv is None else argv
    environment = os.environ if env is None else env
    correlation_id = uuid.uuid4().hex

    path = store_path(environment)

    _emit("start", correlation_id, "taskmaster run started")

    repository = JsonFileTaskRepository(path, correlation_id)

    try:
        print(_execute(parse_command(arguments), repository, correlation_id))
    except ListingFailed as failure:
        return _fail(correlation_id, render_listing_failed(failure))
    except (InvalidCommand, CreationFailed) as failure:
        return _fail(correlation_id, render_failed(failure))

    _emit("end", correlation_id, "taskmaster run finished")

    return 0


def _execute(command, repository, correlation_id):
    """Dispatch the parsed Command to its use case and render the outcome."""
    if isinstance(command, CreateTaskCommand):
        return render_created(create_task(command, repository, correlation_id))

    return render_task_list(list_tasks(repository, correlation_id))


def _fail(correlation_id, message):
    """Render the failure to the User and report it as a failed run."""
    print(message)
    _emit(
        "error",
        correlation_id,
        "taskmaster run failed",
        level=logging.ERROR,
    )

    return FAILURE_EXIT_CODE


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


if __name__ == "__main__":  # pragma: no cover - process entrypoint
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    sys.exit(main())
