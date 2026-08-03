# REQ-ARCH-020

**TYPE:** ARCH
**ORIGIN:** flowchart subgraph: system

**STATEMENT:** The `system` boundary SHALL contain exactly `cli`, `scheduler`, `tasks`, `spaces`, `notifications`, and `storage`, and expose only the edges crossing to `User`.

**ACCEPTANCE_CRITERIA:**

1. Given the architecture diagram, When the `system` subgraph is inspected, Then it contains exactly those six blocks and no others.
2. Given any edge crossing the `system` boundary, When it is enumerated, Then its counterpart is `User` and no other external actor exists.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
