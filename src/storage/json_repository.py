"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-004]
@sdoc[REQ-FUNC-005]
@sdoc[REQ-ARCH-004]
@sdoc[REQ-ARCH-005]
@sdoc[REQ-ARCH-016]
@sdoc[REQ-ARCH-017]
@sdoc[REQ-ARCH-018]
@sdoc[REQ-ARCH-019]
@sdoc[REQ-ARCH-020]
@sdoc[REQ-ARCH-021]
"""

import hashlib
import json
import os
from datetime import date
from pathlib import Path

from tasks.model import Task
from tasks.repository import LoadResult, SaveResult


class JsonFileRepository:
    """Reads and writes task records as a single local JSON file.

    The fingerprint is a hash of the store's bytes (ADR 0005). A save first
    re-reads the store's current fingerprint and refuses to write on a
    mismatch (ADR 0003), and writes through a temporary file followed by a
    rename so an interrupted write leaves the previous content intact.

    @sdoc[REQ-ARCH-004]
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> LoadResult:
        """@sdoc[REQ-ARCH-016]
        @sdoc[REQ-ARCH-017]
        @sdoc[REQ-ARCH-018]
        @sdoc[REQ-FUNC-004]
        @sdoc[REQ-FUNC-005]
        """
        if not self._path.exists():
            return LoadResult(tasks=[], fingerprint=None)

        raw = self._path.read_bytes()
        try:
            records = json.loads(raw)
        except ValueError:
            return LoadResult(
                tasks=[], fingerprint=None, error="store content is not valid JSON"
            )

        tasks = [
            Task(
                text=r["text"],
                done=r["done"],
                space=r.get("space", ""),
                due_date=(
                    date.fromisoformat(r["due_date"]) if r.get("due_date") else None
                ),
            )
            for r in records
        ]
        return LoadResult(tasks=tasks, fingerprint=self._fingerprint_of(raw))

    def save(self, tasks: list[Task], fingerprint: str | None) -> SaveResult:
        """@sdoc[REQ-ARCH-019]
        @sdoc[REQ-ARCH-020]
        @sdoc[REQ-ARCH-021]
        @sdoc[REQ-FUNC-004]
        @sdoc[REQ-FUNC-005]
        """
        current = self._current_fingerprint()
        if fingerprint != current:
            return SaveResult(ok=False, fingerprint=None)

        payload = json.dumps(
            [
                {
                    "text": t.text,
                    "done": t.done,
                    "space": t.space,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                }
                for t in tasks
            ]
        ).encode("utf-8")
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        tmp_path.write_bytes(payload)
        os.replace(tmp_path, self._path)
        return SaveResult(ok=True, fingerprint=self._fingerprint_of(payload))

    def _current_fingerprint(self) -> str | None:
        if not self._path.exists():
            return None
        return self._fingerprint_of(self._path.read_bytes())

    @staticmethod
    def _fingerprint_of(raw: bytes) -> str:
        return hashlib.sha256(raw).hexdigest()
