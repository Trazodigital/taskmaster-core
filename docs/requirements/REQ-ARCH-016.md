# REQ-ARCH-016

**TYPE:** ARCH
**ORIGIN:** flowchart edge: scheduler -> tasks

**STATEMENT:** Information `due-date check tick` SHALL flow from `scheduler` to `tasks` on each scheduling interval.

**ACCEPTANCE_CRITERIA:**

1. Given a scheduling interval has elapsed, When `scheduler` fires, Then `tasks` receives exactly one due-date check tick per interval.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
