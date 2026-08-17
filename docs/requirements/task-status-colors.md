# Task-status-colors feature requirements

Feature-level requirement for coloring each visible task by its status, derived from the approved
feature sequence diagram at `docs/design/diagrams/task-status-colors.sequence.mmd`. Uses only
`Task`'s existing `done`/`due_date` fields — no new task state.

---

## REQ-FUNC-009 — color each task by its status

REFINES: REQ-ARCH-001, REQ-ARCH-002

SOURCE_DIAGRAM: docs/design/diagrams/task-status-colors.sequence.mmd

STATEMENT: taskmaster-app SHALL render each visible task in red when overdue, in green when done, and in a distinct color when in progress.

RATIONALE: A user scanning the task list today has to read each task's date and done mark to judge its status; a per-task color makes overdue and completed tasks recognizable at a glance.

ACCEPTANCE_CRITERIA:

- Given an overdue task, When the task list is rendered, Then it is shown in red.
- Given a done task, When the task list is rendered, Then it is shown in green, even if its due date is earlier than the current date.
- Given an in-progress task, When the task list is rendered, Then it is shown in a color distinct from both red and green.
- Given the task list is re-rendered after any change, When a task's status has changed, Then its color reflects the new status.
