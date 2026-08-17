# Add-task feature requirements

Feature-level requirement for adding a task, derived from the approved feature sequence diagram at
`docs/design/diagrams/add-task.sequence.mmd`. This is the thinnest vertical slice through the
merged baseline architecture: it exercises `taskmaster-app`, `task-model` and `TaskRepository`
without redeclaring any structural or behavioural invariant the architecture already states.

---

## REQ-FUNC-001 — add a task and persist it

REFINES: REQ-ARCH-001, REQ-ARCH-002, REQ-ARCH-008, REQ-ARCH-009

SOURCE_DIAGRAM: docs/design/diagrams/add-task.sequence.mmd

STATEMENT: The user SHALL be able to enter a task's text through taskmaster-app and have it added to the task list and persisted through TaskRepository.

RATIONALE: This is the thinnest slice that exercises all three declared modules (ui, tasks, storage) end to end, so it proves the merged architecture with real code before any second feature is attempted.

ACCEPTANCE_CRITERIA:

- Given taskmaster-app is running, When the user presses the add key and enters task text, Then task-model builds a new task record marked not done from that text.
- Given a new task record, When taskmaster-app appends it to the in-memory task list, Then it issues a save request to TaskRepository carrying the full task list and the fingerprint held since the last load.
- Given the store's fingerprint has not changed externally, When the save request is processed, Then TaskRepository reports a save outcome confirming success with a new fingerprint, and the new task is shown in the list.
- Given the store's fingerprint has changed externally, When the save request is processed, Then TaskRepository reports the external change, nothing is written, and taskmaster-app reports it to the user instead of showing the new task as saved.
- Given the application is restarted after a successful save, When it loads the store, Then the added task is present in the task list.
