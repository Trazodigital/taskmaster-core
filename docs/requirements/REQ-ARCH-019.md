# REQ-ARCH-019

**TYPE:** ARCH
**ORIGIN:** flowchart subgraph: external

**STATEMENT:** The `external` boundary SHALL contain exactly the `User` actor and expose only the `issues command` and `deliver reminder` edges crossing it.

**ACCEPTANCE_CRITERIA:**

1. Given the architecture diagram, When the `external` subgraph is inspected, Then `User` is its only member.
2. Given any edge crossing the `external` boundary, When it is enumerated, Then it is either `issues command` outbound or `deliver reminder` inbound.

**SOURCE_DIAGRAM_FLOWCHART:** docs/architecture/diagrams/system-overview.flowchart.mmd
**SOURCE_DIAGRAM_SEQUENCE:** docs/architecture/diagrams/system-overview.sequence.mmd
