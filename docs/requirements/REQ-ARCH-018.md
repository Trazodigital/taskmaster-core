# REQ-ARCH-018

**TYPE:** ARCH
**ORIGIN:** flowchart edge: notifications -> User

**STATEMENT:** Information `deliver reminder` SHALL flow from `notifications` to `User` for each reported Overdue Task.

**ACCEPTANCE_CRITERIA:**

1. Given an Overdue Task received by `notifications`, When delivery is dispatched, Then the User receives a Reminder naming the Task and its Due Date.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
