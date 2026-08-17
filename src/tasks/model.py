"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
"""

from dataclasses import dataclass, replace


@dataclass
class Task:
    text: str
    done: bool = False


def new_task(text: str) -> Task:
    return Task(text=text)


def toggle_done(task: Task) -> Task:
    """@sdoc[REQ-FUNC-002]"""
    return replace(task, done=not task.done)
