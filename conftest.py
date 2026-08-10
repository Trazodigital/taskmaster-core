"""Pytest root configuration.

Its only job is to exist: under pytest's default ``prepend`` import mode the
directory holding a ``conftest.py`` is inserted into ``sys.path``, which puts
the repository root there and lets co-located tests under ``src/<module>/tests/``
import their module as ``src.<module>.<name>``.

Without this file each test directory would be added to ``sys.path`` instead,
and those imports would fail.
"""
