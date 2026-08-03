# REQ-ARCH-001

**TYPE:** ARCH
**ORIGIN:** flowchart node: User

**STATEMENT:** The system SHALL treat `User` as an external actor outside the TaskMaster Core trust boundary.

**ACCEPTANCE_CRITERIA:**

1. Given an actor outside the system boundary, When that actor interacts with TaskMaster Core, Then the only inbound path is a Command issued to `cli`.
2. Given a Reminder produced by `notifications`, When it is delivered, Then `User` is the sole recipient outside the boundary.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
