# REQ-ARCH-006

**TYPE:** ARCH
**ORIGIN:** flowchart node: notifications

**STATEMENT:** The system SHALL provide a `notifications` block responsible for delivering a Reminder to the User for an Overdue Task.

**ACCEPTANCE_CRITERIA:**

1. Given an Overdue Task reported by `tasks`, When `notifications` handles it, Then `notifications` delivers exactly one Reminder to the User.
2. Given a Reminder delivery, When it is dispatched, Then `notifications` returns no acknowledgement to `tasks`.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
