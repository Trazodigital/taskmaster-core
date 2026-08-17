# Delete-task feature requirements

Feature-level requirement for removing a task, derived from the approved feature sequence diagram
at `docs/design/diagrams/delete-task.sequence.mmd`. Reuses `taskmaster-app` and `TaskRepository`
exactly as `REQ-FUNC-001` established them. Unlike `add-task` and `toggle-task`, this feature makes
no call into `task-model`: removing an item from the in-memory list is not a transformation of a
task record, so there is nothing for `task-model` to do.

---

## REQ-FUNC-003 — delete a task and persist it

REFINES: REQ-ARCH-001, REQ-ARCH-008, REQ-ARCH-009

SOURCE_DIAGRAM: docs/design/diagrams/delete-task.sequence.mmd

STATEMENT: The user SHALL be able to remove an existing task through taskmaster-app and have the change persisted through TaskRepository.

RATIONALE: Add and toggle both grow or mark the list; without delete, a mistaken or stale task can never leave it. This is the last of the three basic list operations before the app needs anything beyond a flat list.

ACCEPTANCE_CRITERIA:

- Given taskmaster-app is running with at least one task shown, When the user selects a task and presses the delete key, Then taskmaster-app removes it from the in-memory task list.
- Given the reduced task list, When taskmaster-app has removed the task, Then it issues a save request to TaskRepository carrying the full remaining task list and the fingerprint held since the last load.
- Given the store's fingerprint has not changed externally, When the save request is processed, Then TaskRepository reports a save outcome confirming success with a new fingerprint, and the list no longer shows the deleted task.
- Given the store's fingerprint has changed externally, When the save request is processed, Then TaskRepository reports the external change, nothing is written, and taskmaster-app reports it to the user instead of showing the deletion as saved.
- Given the application is restarted after a successful delete, When it loads the store, Then the deleted task is absent from the task list.
