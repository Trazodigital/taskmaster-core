"""Rendering of a created Task back to the User.

@sdoc[REQ-FUNC-001]
"""

from src.cli.presenter import render_created
from src.tasks.create_task import Task


def test_confirmation_carries_the_persisted_identifier():
    """The User sees the identifier storage assigned.

    @sdoc[REQ-FUNC-001]
    """
    message = render_created(Task(id="42", title="buy milk"))

    assert "42" in message
    assert "buy milk" in message
