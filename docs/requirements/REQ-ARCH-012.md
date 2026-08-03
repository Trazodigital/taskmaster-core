# REQ-ARCH-012

**TYPE:** ARCH
**ORIGIN:** flowchart edge: tasks -> storage

**STATEMENT:** Information `persist task` SHALL flow from `tasks` to `storage` whenever a Task is created or modified.

**ACCEPTANCE_CRITERIA:**

1. Given a created or modified Task, When `tasks` completes its domain logic, Then `tasks` sends the Task to `storage` and awaits a persisted identifier.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
