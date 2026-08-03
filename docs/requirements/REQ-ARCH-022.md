# REQ-ARCH-022

**TYPE:** ARCH
**ORIGIN:** sequence Flow 1: write timeout note

**STATEMENT:** A `persist task` write SHALL time out after 5 seconds and SHALL NOT be retried automatically.

**ACCEPTANCE_CRITERIA:**

1. Given a `storage` write that does not complete, When 5 seconds elapse, Then `tasks` abandons the write and treats it as a storage error.
2. Given an abandoned write, When the failure is handled, Then no automatic retry is issued.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
