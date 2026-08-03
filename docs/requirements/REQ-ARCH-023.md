# REQ-ARCH-023

**TYPE:** ARCH
**ORIGIN:** sequence Flow 2: alt no tasks stored

**STATEMENT:** A `list tasks` operation over an empty store SHALL return an empty Task List rather than an error.

**ACCEPTANCE_CRITERIA:**

1. Given `storage` returns no stored Tasks, When `tasks` builds the response, Then `tasks` returns an empty Task List to `cli`.
2. Given an empty Task List, When `cli` renders it, Then the User receives an empty-state message and no error.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
