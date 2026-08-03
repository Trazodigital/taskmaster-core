# REQ-ARCH-028

**TYPE:** ARCH
**ORIGIN:** sequence Flow 4: loop

**STATEMENT:** Exactly one Reminder SHALL be produced per Overdue Task found in a single due-date check.

**ACCEPTANCE_CRITERIA:**

1. Given a due-date check finds N Overdue Tasks, When the check completes, Then exactly N `task due-date reached` messages are emitted.
2. Given a Task that is not overdue, When the check runs, Then no Reminder is produced for it.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
