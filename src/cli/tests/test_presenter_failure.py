"""Rendering a creation failure back to the User.

@sdoc[REQ-FUNC-003]
"""

from src.cli.presenter import render_failed
from src.tasks.create_task import CreationFailed


def test_failure_is_explicit_and_carries_no_confirmation():
    """The User is told it failed, never that a task was created.

    @sdoc[REQ-FUNC-003]
    """
    message = render_failed(CreationFailed("disk unavailable"))

    assert "disk unavailable" in message
    assert message.lower().startswith("could not create")
    assert "Created task" not in message
