"""Render the outcome of a create-task Command back to the User.

@sdoc[REQ-FUNC-001]
"""


def render_created(task):
    """Confirmation line carrying the identifier storage assigned.

    @sdoc[REQ-FUNC-001]
    """
    return f"Created task {task.id}: {task.title}"
