# REQ-NFR-PERF-002

**TYPE:** NFR-PERF
**ORIGIN:** sequence Flow 1 — persist task under the write-timeout invariant
**COVERS:** REQ-ARCH-012, REQ-ARCH-021, REQ-ARCH-022

**STATEMENT:** A `persist task` write SHALL complete well inside the 5-second timeout declared by REQ-ARCH-022, so that the timeout is an error boundary rather than an expected outcome.

**ACCEPTANCE_CRITERIA:**

1. Given a Task submitted to `storage`, When the write completes, Then the elapsed write duration is at or below the declared threshold at the 99th percentile.
2. Given the declared threshold is met, When REQ-ARCH-022 is evaluated, Then the 5-second timeout is reached only under storage failure and never under nominal load.

METRIC: p99 task persistence write duration
THRESHOLD: <= 1000 ms
MEASUREMENT_METHOD:
  INSTRUMENT: bench
  WINDOW: per-release
  SAMPLE: >= 1000 writes

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
