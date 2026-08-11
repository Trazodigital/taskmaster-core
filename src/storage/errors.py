"""Failures raised by adapters of the ``task-repository`` port.

Declaring the error here rather than inside a concrete adapter keeps ``tasks``
independent of which adapter is wired in: the use case handles one exception
type whether the write went to a JSON file, a database, or a test double.

@sdoc[REQ-FUNC-003]
"""


class StorageError(Exception):
    """A durable write could not be completed."""
