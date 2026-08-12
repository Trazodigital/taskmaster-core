# REQ-ARCH-005

**TYPE:** ARCH
**ORIGIN:** flowchart node: spaces

**STATEMENT:** The system SHALL provide a `spaces` block responsible for Space creation, Space membership, and assignment of a Task to a Space.

**ACCEPTANCE_CRITERIA:**

1. Given an assign-task-to-space operation, When `spaces` handles it, Then `spaces` verifies the target Space exists before writing.
2. Given a verified Space, When the assignment is applied, Then `spaces` persists the Space through `storage` and returns the updated Space.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
