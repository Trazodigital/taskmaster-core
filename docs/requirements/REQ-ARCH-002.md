# REQ-ARCH-002

**TYPE:** ARCH
**ORIGIN:** flowchart node: cli

**STATEMENT:** The system SHALL provide a `cli` block responsible for translating a Command from the User into exactly one task or space operation.

**ACCEPTANCE_CRITERIA:**

1. Given a User issuing a Command, When `cli` receives it, Then `cli` dispatches exactly one operation to `tasks` or `spaces`.
2. Given an operation result, When `cli` receives it, Then `cli` returns a rendered result to the User.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
