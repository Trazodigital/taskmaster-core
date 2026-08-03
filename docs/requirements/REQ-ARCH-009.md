# REQ-ARCH-009

**TYPE:** ARCH
**ORIGIN:** flowchart edge: cli -> tasks

**STATEMENT:** Information `create task` SHALL flow from `cli` to `tasks` when the issued Command is a task-creation Command.

**ACCEPTANCE_CRITERIA:**

1. Given a task-creation Command, When `cli` dispatches it, Then `tasks` receives the Task payload and `spaces` is not invoked.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
