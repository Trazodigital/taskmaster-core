"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-ARCH-003]
"""

from dataclasses import dataclass
from typing import Protocol

from tasks.model import Task


@dataclass
class LoadResult:
    tasks: list[Task]
    fingerprint: str | None
    error: str | None = None


@dataclass
class SaveResult:
    ok: bool
    fingerprint: str | None


class TaskRepository(Protocol):
    def load(self) -> LoadResult: ...

    def save(self, tasks: list[Task], fingerprint: str | None) -> SaveResult: ...
