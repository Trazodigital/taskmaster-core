# REQ-ARCH-003

**TYPE:** ARCH
**ORIGIN:** flowchart node: scheduler

**STATEMENT:** The system SHALL provide a `scheduler` block responsible for periodically triggering Due Date evaluation in `tasks`.

**ACCEPTANCE_CRITERIA:**

1. Given the system is running, When a scheduling interval elapses, Then `scheduler` sends exactly one due-date check tick to `tasks`.
2. Given a due-date check tick was sent, When `tasks` completes the check, Then `scheduler` receives a completion acknowledgement.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
