# REQ-ARCH-025

**TYPE:** ARCH
**ORIGIN:** sequence Flow 3: alt space not found

**STATEMENT:** An assignment naming a non-existent Space SHALL surface to the User as an unknown-space error.

**ACCEPTANCE_CRITERIA:**

1. Given verification finds no matching Space, When `spaces` responds, Then `spaces` returns an unknown-space result to `cli`.
2. Given an unknown-space result, When `cli` renders it, Then the User receives an error message and no confirmation.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
