# REQ-ARCH-014

**TYPE:** ARCH
**ORIGIN:** flowchart edge: spaces -> storage

**STATEMENT:** Information `persist space` SHALL flow from `spaces` to `storage` whenever a Space is created or modified.

**ACCEPTANCE_CRITERIA:**

1. Given a verified Space assignment, When `spaces` applies it, Then `spaces` sends the Space to `storage` and awaits a persisted identifier.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
