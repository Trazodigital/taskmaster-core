# REQ-ARCH-007

**TYPE:** ARCH
**ORIGIN:** flowchart node: storage

**STATEMENT:** The system SHALL provide a `storage` block responsible for persisting and loading Tasks and Spaces.

**ACCEPTANCE_CRITERIA:**

1. Given a persist request from `tasks` or `spaces`, When `storage` handles it, Then `storage` returns the persisted identifier or a storage error.
2. Given a load request from `tasks` or `spaces`, When `storage` handles it, Then `storage` returns the stored records or a storage error.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
