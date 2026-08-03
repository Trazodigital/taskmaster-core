# REQ-ARCH-017

**TYPE:** ARCH
**ORIGIN:** flowchart edge: tasks -> notifications

**STATEMENT:** Information `task due-date reached` SHALL flow from `tasks` to `notifications` for each Overdue Task found during a due-date check.

**ACCEPTANCE_CRITERIA:**

1. Given a due-date check identifying an Overdue Task, When `tasks` reports it, Then `notifications` receives the Overdue Task identity and its Due Date.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
