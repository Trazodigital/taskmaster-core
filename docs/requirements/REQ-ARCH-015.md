# REQ-ARCH-015

**TYPE:** ARCH
**ORIGIN:** flowchart edge: spaces -> storage

**STATEMENT:** Information `load spaces` SHALL flow from `spaces` to `storage` whenever Space existence must be verified.

**ACCEPTANCE_CRITERIA:**

1. Given an assign-task-to-space operation, When `spaces` begins handling it, Then `spaces` requests stored Spaces from `storage` before any write.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
