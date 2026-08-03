# REQ-NFR-SEC-001

**TYPE:** NFR-SEC
**ORIGIN:** flowchart subgraphs — trust boundary between `external` and `system`
**COVERS:** REQ-ARCH-001, REQ-ARCH-019, REQ-ARCH-020, REQ-ARCH-007

**STATEMENT:** No block inside the `system` trust boundary SHALL carry a high-severity security finding, given that `storage` holds every Task and Space in the product.

**ACCEPTANCE_CRITERIA:**

1. Given the modules composing the `system` boundary, When the security scan runs over them, Then it reports no high-severity finding.
2. Given a new module is added inside the `system` boundary, When the scan runs, Then that module is included in the scanned set and held to the same threshold.

METRIC: count of high-severity security-scan findings
THRESHOLD: == 0 findings
MEASUREMENT_METHOD:
  INSTRUMENT: security-scan
  WINDOW: per-release
  SAMPLE: all modules under src/

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
