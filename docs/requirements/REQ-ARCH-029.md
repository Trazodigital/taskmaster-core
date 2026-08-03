# REQ-ARCH-029

**TYPE:** ARCH
**ORIGIN:** sequence Flow 4: tick acknowledgement

**STATEMENT:** A `due-date check tick` SHALL be acknowledged to `scheduler` once the check completes, independently of Reminder delivery outcomes.

**ACCEPTANCE_CRITERIA:**

1. Given a due-date check tick, When `tasks` finishes evaluating stored Tasks, Then `tasks` returns a completion acknowledgement to `scheduler`.
2. Given one or more Reminder deliveries were unconfirmed, When the check completes, Then the acknowledgement is still returned.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
