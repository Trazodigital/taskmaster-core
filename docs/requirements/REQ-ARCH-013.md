# REQ-ARCH-013

**TYPE:** ARCH
**ORIGIN:** flowchart edge: tasks -> storage

**STATEMENT:** Information `load tasks` SHALL flow from `tasks` to `storage` whenever stored Tasks are required.

**ACCEPTANCE_CRITERIA:**

1. Given a list-tasks operation or a due-date check tick, When `tasks` needs stored state, Then `tasks` requests Tasks from `storage` rather than serving them from memory.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
