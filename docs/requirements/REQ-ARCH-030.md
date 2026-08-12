# REQ-ARCH-030

**TYPE:** ARCH
**ORIGIN:** flowchart edge: cli -> spaces (create space)

**STATEMENT:** Information `create space` SHALL flow from `cli` to `spaces` when the issued Command creates a Space.

**ACCEPTANCE_CRITERIA:**

1. Given a Command that creates a Space, When `cli` dispatches it, Then `spaces` receives the Space name and returns the created Space or an explicit failure.
2. Given the created Space, When `cli` renders the result, Then the User receives a confirmation carrying the persisted Space identifier.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
