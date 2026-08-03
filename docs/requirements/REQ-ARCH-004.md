# REQ-ARCH-004

**TYPE:** ARCH
**ORIGIN:** flowchart node: tasks

**STATEMENT:** The system SHALL provide a `tasks` block responsible for Task lifecycle and Due Date evaluation.

**ACCEPTANCE_CRITERIA:**

1. Given a create-task operation from `cli`, When `tasks` handles it, Then `tasks` persists the Task through `storage` and returns the created Task.
2. Given a list-tasks operation from `cli`, When `tasks` handles it, Then `tasks` loads Tasks through `storage` and returns a Task List.
3. Given a due-date check tick, When `tasks` evaluates stored Tasks, Then every Overdue Task is reported to `notifications`.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
