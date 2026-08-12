"""File-backed adapter for the ``task-repository`` port.

Declared in ``docs/architecture/system-overview.md`` as the real adapter for
that port: Tasks are stored as one JSON document on the local filesystem, so a
Task outlives the process that created it.

Every persist is a whole-file read-modify-write. Two invariants make that safe
enough for the single-user CLI of @adr[0001]: a store that cannot be parsed is
never written over, and a new document only becomes visible through an atomic
rename.

Emits the structured runtime events required by
``tech-stack-integrations/observability-platform.yaml``, so these REQs carry no
``@no-runtime-events`` opt-out.

@sdoc[REQ-FUNC-004]
@sdoc[REQ-FUNC-005]
@sdoc[REQ-FUNC-006]
@adr[0001]
@adr[0005]
"""

import json
import logging
import os
import tempfile
from pathlib import Path

from src.storage.errors import StorageError

_LOGGER = logging.getLogger("taskmaster.storage")
_FEATURE = "storage"


class JsonFileTaskRepository:
    """Satisfies the task-repository port with a JSON file on disk."""

    def __init__(self, store_path, correlation_id):
        self._store_path = Path(store_path)
        self._correlation_id = correlation_id

    def persist(self, title):
        """Append the Task to the store and return the identifier assigned.

        Raises ``StorageError`` when the store cannot be read or the new
        document cannot be written; in both cases the file on disk is left
        exactly as it was.

        @sdoc[REQ-FUNC-004]
        """
        self._emit("start", "REQ-FUNC-004", "task persistence requested")

        tasks = self._read()
        task_id = str(len(tasks) + 1)
        self._write(tasks + [{"id": task_id, "title": title}])

        self._emit("end", "REQ-FUNC-004", "task persisted")

        return task_id

    def load(self):
        """Return every stored Task, oldest first; an absent store is empty.

        @sdoc[REQ-FUNC-004]
        """
        return self._read()

    def _read(self):
        """Read the whole store, refusing to guess at content it cannot parse.

        Failing here rather than further down is what keeps the original bytes
        recoverable: nothing is written until the existing document is known
        to be a Task list.

        @sdoc[REQ-FUNC-005]
        """
        try:
            content = self._store_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            # A first run has no store yet. Every other read failure means the
            # Tasks exist and are unreachable, which is not an empty store.
            return []
        except OSError as exc:
            self._fail("REQ-FUNC-006", "store could not be read", exc)

        try:
            tasks = json.loads(content)
        except json.JSONDecodeError as exc:
            self._fail("REQ-FUNC-005", "stored content is not valid json", exc)

        if not isinstance(tasks, list):
            self._fail(
                "REQ-FUNC-005",
                "stored content is not a task list",
                TypeError(f"expected a list, found {type(tasks).__name__}"),
            )

        return tasks

    def _write(self, tasks):
        """Promote a new store document with an atomic replace.

        The temporary file is a sibling of the store because ``os.replace`` is
        only atomic within one filesystem.

        @sdoc[REQ-FUNC-004]
        @sdoc[REQ-FUNC-006]
        @adr[0005]
        """
        handle, temporary = tempfile.mkstemp(
            dir=str(self._store_path.parent),
            prefix=f".{self._store_path.name}.",
        )
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as document:
                json.dump(tasks, document)
            os.replace(temporary, self._store_path)
        except OSError as exc:
            # The store itself was never opened for writing, so whatever it
            # held before this call it still holds.
            self._discard(temporary)
            self._fail("REQ-FUNC-006", "store could not be written", exc)
        except BaseException:
            self._discard(temporary)
            raise

    @staticmethod
    def _discard(temporary):
        """Drop a temporary document that never became the store."""
        try:
            os.unlink(temporary)
        except OSError:
            # An orphan temporary file is the cost @adr[0005] accepts; it must
            # never mask the failure being reported.
            pass

    def _fail(self, req_uid, reason, cause):
        """Report a storage failure and stop. No retry is ever issued."""
        self._emit("error", req_uid, reason, level=logging.ERROR)

        raise StorageError(f"{reason}: {cause}") from cause

    def _emit(self, event_type, req_uid, message, level=logging.INFO):
        """Emit one structured runtime event with the required fields."""
        _LOGGER.log(
            level,
            message,
            extra={
                "event_type": event_type,
                "feature": _FEATURE,
                "req_uid": req_uid,
                "correlation_id": self._correlation_id,
            },
        )
