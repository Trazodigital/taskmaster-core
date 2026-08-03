# REQ-NFR-PERF-001

**TYPE:** NFR-PERF
**ORIGIN:** sequence Flow 4 — reminder dispatch following a due-date check tick
**COVERS:** REQ-ARCH-016, REQ-ARCH-017, REQ-ARCH-018, REQ-ARCH-028

**STATEMENT:** A Reminder SHALL be dispatched within a bounded latency of the due-date check tick that identified its Overdue Task.

**ACCEPTANCE_CRITERIA:**

1. Given a due-date check tick that identifies one Overdue Task, When `notifications` dispatches the Reminder, Then the elapsed time from tick receipt to dispatch is at or below the declared threshold at the 95th percentile.
2. Given a due-date check tick that identifies many Overdue Tasks, When the check completes, Then the threshold is evaluated per Reminder and not against the batch total.

METRIC: p95 reminder dispatch latency
THRESHOLD: <= 500 ms
MEASUREMENT_METHOD:
  INSTRUMENT: bench
  WINDOW: per-release
  SAMPLE: >= 100 scheduler ticks

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
