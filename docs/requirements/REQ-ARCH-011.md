# REQ-ARCH-011

**TYPE:** ARCH
**ORIGIN:** flowchart edge: cli -> spaces

**STATEMENT:** Information `assign task to space` SHALL flow from `cli` to `spaces` when the issued Command assigns a Task to a Space.

**ACCEPTANCE_CRITERIA:**

1. Given an assignment Command carrying a Task identifier and a Space identifier, When `cli` dispatches it, Then `spaces` receives both identifiers.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
