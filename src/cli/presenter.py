"""Render the outcome of a create-task Command back to the User.

@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-003]
@sdoc[REQ-FUNC-007]
"""

#: Shown for an empty Task List, which is a normal state and not a failure.
NO_TASKS = "No tasks yet."


def render_created(task):
    """Confirmation line carrying the identifier storage assigned.

    @sdoc[REQ-FUNC-001]
    """
    return f"Created task {task.id}: {task.title}"


def render_failed(failure):
    """Explicit failure line, carrying no confirmation wording.

    @sdoc[REQ-FUNC-003]
    """
    return f"Could not create the task: {failure}"


def render_task_list(tasks):
    """One line per stored Task, oldest first; an empty list says so plainly.

    @sdoc[REQ-FUNC-007]
    """
    if not tasks:
        return NO_TASKS

    return "\n".join(f"{task.id}: {task.title}" for task in tasks)


def render_listing_failed(failure):
    """Explicit failure line for a Task List that could not be read.

    An unreadable store must never render as an empty Task List — the two
    outcomes look identical to the User otherwise.

    @sdoc[REQ-FUNC-007]
    """
    return f"Could not list the tasks: {failure}"
