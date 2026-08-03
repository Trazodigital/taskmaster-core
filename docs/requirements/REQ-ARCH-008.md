# REQ-ARCH-008

**TYPE:** ARCH
**ORIGIN:** flowchart edge: User -> cli

**STATEMENT:** Information `issues command` SHALL flow from `User` to `cli` when the User invokes TaskMaster Core.

**ACCEPTANCE_CRITERIA:**

1. Given a User at the system boundary, When the User issues a Command, Then `cli` receives the Command and no other block is reached directly.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
