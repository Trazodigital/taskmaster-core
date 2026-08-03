# REQ-ARCH-026

**TYPE:** ARCH
**ORIGIN:** sequence Flow 4: fire-and-forget note

**STATEMENT:** The `task due-date reached` message SHALL be fire-and-forget and SHALL NOT block the due-date check on an acknowledgement.

**ACCEPTANCE_CRITERIA:**

1. Given `tasks` reports an Overdue Task, When the message is sent, Then `tasks` continues the check without awaiting a response from `notifications`.
2. Given `notifications` is unavailable, When the message is sent, Then the due-date check still completes.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
