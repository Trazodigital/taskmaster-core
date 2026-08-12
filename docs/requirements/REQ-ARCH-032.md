# REQ-ARCH-032

**TYPE:** ARCH
**ORIGIN:** sequence Flow 5: load spaces before persist space

**STATEMENT:** A `create space` operation SHALL observe `load spaces` strictly before any `persist space` write.

**ACCEPTANCE_CRITERIA:**

1. Given a `create space` operation, When `spaces` begins handling it, Then `spaces` requests stored Spaces from `storage` before any write.
2. Given the stored Spaces have not been loaded, When `spaces` handles the operation, Then no `persist space` write is issued.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
