"""Inbound intake of a create-task Command at the trust boundary.

Serves the ``command-input`` port declared in
``docs/architecture/system-overview.md``: it turns raw CLI arguments into a
validated Command, or rejects them before any other module is reached. The
rejection happening here — rather than in ``tasks`` or ``storage`` — is what
keeps an invalid title from ever producing a persist call.

Pure validation: no state is mutated and no port is called, so this REQ emits
no runtime events and carries the structured-logging opt-out.

@sdoc[REQ-FUNC-002]
@no-runtime-events[REQ-FUNC-002]
"""

from dataclasses import dataclass


class InvalidCommand(Exception):
    """A Command could not be built from the given arguments."""


@dataclass(frozen=True)
class CreateTaskCommand:
    """A validated request to create a Task."""

    title: str


def parse_create_task(title):
    """Build a CreateTaskCommand, rejecting a missing or blank title.

    A title of whitespace only is treated as blank: it would render as an
    unaddressable Task for the User.

    @sdoc[REQ-FUNC-002]
    """
    if title is None or not title.strip():
        raise InvalidCommand("a task title is required")

    return CreateTaskCommand(title.strip())
