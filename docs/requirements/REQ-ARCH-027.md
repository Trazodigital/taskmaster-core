# REQ-ARCH-027

**TYPE:** ARCH
**ORIGIN:** sequence Flow 4: fire-and-forget note

**STATEMENT:** The `deliver reminder` message SHALL be fire-and-forget and delivery SHALL NOT be treated as confirmed.

**ACCEPTANCE_CRITERIA:**

1. Given `notifications` dispatches a Reminder, When dispatch returns, Then no delivery confirmation is recorded.
2. Given delivery cannot be confirmed, When the system reports state, Then it SHALL NOT claim the User received the Reminder.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
