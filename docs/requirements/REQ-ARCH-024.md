# REQ-ARCH-024

**TYPE:** ARCH
**ORIGIN:** sequence Flow 3: ordering

**STATEMENT:** A Space SHALL be verified to exist via `load spaces` before any `persist space` write is issued.

**ACCEPTANCE_CRITERIA:**

1. Given an assign-task-to-space operation, When `spaces` handles it, Then `load spaces` is observed strictly before `persist space`.
2. Given the Space does not exist, When verification completes, Then no `persist space` write is issued at all.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
