# REQ-ARCH-010

**TYPE:** ARCH
**ORIGIN:** flowchart edge: cli -> tasks

**STATEMENT:** Information `list tasks` SHALL flow from `cli` to `tasks` when the issued Command is a task-listing Command.

**ACCEPTANCE_CRITERIA:**

1. Given a task-listing Command, When `cli` dispatches it, Then `tasks` receives the query and returns a Task List.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
