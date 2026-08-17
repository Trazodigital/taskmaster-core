"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
@sdoc[REQ-FUNC-004]
@sdoc[REQ-FUNC-005]
@sdoc[REQ-FUNC-006]
"""

from dataclasses import dataclass, replace
from datetime import date, timedelta


@dataclass
class Task:
    text: str
    done: bool = False
    space: str = ""
    due_date: date | None = None


def new_task(raw_text: str) -> Task:
    """@sdoc[REQ-FUNC-004]
    @sdoc[REQ-FUNC-005]
    """
    tokens = raw_text.split(" ")
    space = ""
    due_date: date | None = None

    while tokens:
        candidate = tokens[-1]
        if candidate.startswith("@"):
            space = candidate[1:]
            tokens.pop()
            continue
        if candidate.startswith("!"):
            try:
                due_date = date.fromisoformat(candidate[1:])
            except ValueError:
                break
            tokens.pop()
            continue
        break

    text = " ".join(tokens) if tokens else raw_text
    return Task(text=text, space=space, due_date=due_date)


def build_task(*, text: str, space: str, due_date: str) -> Task:
    """@sdoc[REQ-FUNC-006]

    Builds a task from already-distinct field values (the structured add
    form), as opposed to `new_task`'s single-string tag parsing. A due_date
    that is empty or does not parse is dropped rather than blocking creation
    or crashing — the same crash-safety posture new_task's own date tag has.
    """
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = date.fromisoformat(due_date)
        except ValueError:
            pass
    return Task(text=text, space=space, due_date=parsed_due_date)


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


def due_today(tasks: list[Task], today: date) -> list[Task]:
    """@sdoc[REQ-FUNC-005]"""
    return [t for t in tasks if not t.done and t.due_date == today]


def due_this_week(tasks: list[Task], today: date) -> list[Task]:
    """@sdoc[REQ-FUNC-005]"""
    week_end = today + timedelta(days=6)
    return [
        t
        for t in tasks
        if not t.done and t.due_date and today <= t.due_date <= week_end
    ]


def overdue(tasks: list[Task], today: date) -> list[Task]:
    """@sdoc[REQ-FUNC-005]"""
    return [t for t in tasks if not t.done and t.due_date and t.due_date < today]
