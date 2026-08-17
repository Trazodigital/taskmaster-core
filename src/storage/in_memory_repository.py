"""
@sdoc[REQ-FUNC-001]
"""

from tasks.model import Task
from tasks.repository import LoadResult, SaveResult


class InMemoryRepository:
    def __init__(self) -> None:
        self._tasks: list[Task] = []
        self._fingerprint: str | None = None
        self._next_fingerprint = 0

    def load(self) -> LoadResult:
        return LoadResult(tasks=list(self._tasks), fingerprint=self._fingerprint)

    def save(self, tasks: list[Task], fingerprint: str | None) -> SaveResult:
        if fingerprint != self._fingerprint:
            return SaveResult(ok=False, fingerprint=None)

        self._next_fingerprint += 1
        self._fingerprint = str(self._next_fingerprint)
        self._tasks = list(tasks)
        return SaveResult(ok=True, fingerprint=self._fingerprint)
