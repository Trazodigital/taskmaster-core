"""Render the outcome of a create-task Command back to the User.

@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-003]
"""


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
