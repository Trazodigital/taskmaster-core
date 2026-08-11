"""In-memory adapter for the ``task-repository`` port.

Declared in ``docs/architecture/system-overview.md`` as the test double for
that port. Keeping Tasks in a dict is what lets the create-task use case be
exercised without touching disk, which is the whole point of the port existing.

@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-007]
"""


class InMemoryTaskRepository:
    """Satisfies the task-repository port without durable storage."""

    def __init__(self):
        self._titles = {}

    def persist(self, title):
        """Store the title and return the identifier assigned to it."""
        task_id = str(len(self._titles) + 1)
        self._titles[task_id] = title

        return task_id

    def load(self):
        """Return every stored Task in the order it was persisted.

        Mirrors the shape the file-backed adapter reads off disk, so a use
        case cannot tell the two apart.

        @sdoc[REQ-FUNC-007]
        """
        items = self._titles.items()

        return [{"id": key, "title": title} for key, title in items]

    def stored(self, task_id):
        """Return the title stored under ``task_id``, or None."""
        return self._titles.get(task_id)
