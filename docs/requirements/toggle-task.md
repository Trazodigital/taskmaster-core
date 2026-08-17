# Toggle-task feature requirements

Feature-level requirement for marking a task done or not done, derived from the approved feature
sequence diagram at `docs/design/diagrams/toggle-task.sequence.mmd`. Reuses `taskmaster-app`,
`task-model`, and `TaskRepository` exactly as `REQ-FUNC-001` established them — no new module,
port, or adapter.

---

## REQ-FUNC-002 — toggle a task's done state and persist it

REFINES: REQ-ARCH-001, REQ-ARCH-002, REQ-ARCH-008, REQ-ARCH-009

SOURCE_DIAGRAM: docs/design/diagrams/toggle-task.sequence.mmd

STATEMENT: The user SHALL be able to flip an existing task's done state through taskmaster-app and have the change persisted through TaskRepository.

RATIONALE: Adding a task without ever being able to complete it makes the list append-only — the smallest change that turns the architecture proof from REQ-FUNC-001 into a usable app is letting a task leave the list of things still to do.

ACCEPTANCE_CRITERIA:

- Given taskmaster-app is running with at least one task shown, When the user selects a task and presses the toggle key, Then task-model flips that task's done state and returns the updated record.
- Given the updated task record, When taskmaster-app replaces it in the in-memory task list, Then it issues a save request to TaskRepository carrying the full task list and the fingerprint held since the last load.
- Given the store's fingerprint has not changed externally, When the save request is processed, Then TaskRepository reports a save outcome confirming success with a new fingerprint, and the list reflects the new done state.
- Given the store's fingerprint has changed externally, When the save request is processed, Then TaskRepository reports the external change, nothing is written, and taskmaster-app reports it to the user instead of showing the toggle as saved.
- Given the application is restarted after a successful toggle, When it loads the store, Then the task's done state is the one it was toggled to.
