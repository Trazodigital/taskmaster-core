"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
@sdoc[REQ-FUNC-004]
"""

from dataclasses import dataclass, replace


@dataclass
class Task:
    text: str
    done: bool = False
    space: str = ""


def new_task(raw_text: str) -> Task:
    """@sdoc[REQ-FUNC-004]"""
    text, _, tag = raw_text.rpartition(" @")
    if text:
        return Task(text=text, space=tag)
    return Task(text=raw_text)


def toggle_done(task: Task) -> Task:
    """@sdoc[REQ-FUNC-002]"""
    return replace(task, done=not task.done)


def distinct_spaces(tasks: list[Task]) -> list[str]:
    """@sdoc[REQ-FUNC-004]"""
    seen = {task.space for task in tasks if task.space}
    return sorted(seen)


def by_space(tasks: list[Task], space: str) -> list[Task]:
    """@sdoc[REQ-FUNC-004]"""
    return [task for task in tasks if task.space == space]
