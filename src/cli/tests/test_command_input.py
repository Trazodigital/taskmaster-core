"""Create-task command validation at the CLI trust boundary.

@sdoc[REQ-FUNC-002]
"""

import pytest

from src.cli.command_input import CreateTaskCommand, InvalidCommand
from src.cli.command_input import parse_create_task
from src.storage.in_memory import InMemoryTaskRepository
from src.tasks.create_task import create_task


@pytest.mark.parametrize("title", [None, "", "   ", "\t\n"])
def test_missing_or_blank_title_is_rejected(title):
    """A missing or blank title never yields a command.

    @sdoc[REQ-FUNC-002]
    """
    with pytest.raises(InvalidCommand):
        parse_create_task(title)


def test_title_is_accepted_and_trimmed():
    """Surrounding whitespace is not part of the Task title.

    @sdoc[REQ-FUNC-002]
    """
    command = parse_create_task("  buy milk  ")

    assert isinstance(command, CreateTaskCommand)
    assert command.title == "buy milk"


def test_rejected_command_never_reaches_the_repository():
    """Rejection happens before tasks or storage are involved.

    @sdoc[REQ-FUNC-002]
    """
    repository = InMemoryTaskRepository()

    with pytest.raises(InvalidCommand):
        create_task(parse_create_task("   "), repository, "corr-1")

    assert repository.stored("1") is None
