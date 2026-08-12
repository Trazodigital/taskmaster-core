# REQ-ARCH-031

**TYPE:** ARCH
**ORIGIN:** sequence Flow 5: alt space name already taken

**STATEMENT:** A `create space` Command naming a Space that already exists SHALL be rejected as a duplicate without issuing any `persist space` write.

**ACCEPTANCE_CRITERIA:**

1. Given a stored Space already carries the requested name, When `spaces` completes verification, Then `spaces` returns a duplicate-space result to `cli`.
2. Given a duplicate-space result, When the operation ends, Then no `persist space` write is issued at all.
3. Given a duplicate-space result, When `cli` renders it, Then the User receives an error message and no confirmation.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
