"""End to end: a Task created in one run is present in the next.

Two separate processes are the whole point — a single in-process test would
prove nothing about durability, only about a shared object.

@sdoc[REQ-FUNC-007]
"""

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(store, *arguments):
    """Run the taskmaster entrypoint as its own process against ``store``."""
    return subprocess.run(
        [sys.executable, "-m", "src.app.main", *arguments],
        cwd=REPO_ROOT,
        env={"PATH": "/usr/bin:/bin", "TASKMASTER_STORE_PATH": str(store)},
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_a_task_created_in_one_run_is_listed_by_the_next(tmp_path):
    """The store outlives the process that wrote it.

    @sdoc[REQ-FUNC-007]
    """
    store = tmp_path / "tasks.json"

    created = _run(store, "create", "buy milk")
    listed = _run(store, "list")

    assert created.returncode == 0, created.stderr
    assert "Created task" in created.stdout
    assert listed.returncode == 0, listed.stderr
    assert "buy milk" in listed.stdout


def test_listing_an_absent_store_is_empty_and_not_an_error(tmp_path):
    """A first run has nothing stored, which is not a failure.

    @sdoc[REQ-FUNC-007]
    """
    listed = _run(tmp_path / "never-written.json", "list")

    assert listed.returncode == 0, listed.stderr
    assert "buy milk" not in listed.stdout
