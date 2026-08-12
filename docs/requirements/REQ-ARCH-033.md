# REQ-ARCH-033

**TYPE:** ARCH
**ORIGIN:** sequence Flow 5: else storage unavailable

**STATEMENT:** A failed `persist space` write SHALL surface to the User as an explicit error rather than a silent success.

**ACCEPTANCE_CRITERIA:**

1. Given `storage` returns a storage error on `persist space`, When `spaces` receives it, Then `spaces` returns a creation failure to `cli`.
2. Given a creation failure, When `cli` renders it, Then the User receives an error message and no confirmation.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
