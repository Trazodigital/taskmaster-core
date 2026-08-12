# REQ-ARCH-034

**TYPE:** ARCH
**ORIGIN:** sequence Flow 3 and Flow 5: write timeout note on persist space

**STATEMENT:** A `persist space` write SHALL time out after 5 seconds and SHALL NOT be retried automatically.

**ACCEPTANCE_CRITERIA:**

1. Given a `storage` write of a Space that does not complete, When 5 seconds elapse, Then `spaces` abandons the write and treats it as a storage error.
2. Given an abandoned `persist space` write, When the failure is handled, Then no automatic retry is issued.
3. Given the same budget governs `persist task` under REQ-ARCH-022, When either write is issued, Then both are bounded by the same 5-second limit.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
