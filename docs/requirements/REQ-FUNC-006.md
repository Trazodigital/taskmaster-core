# REQ-FUNC-006

**TYPE:** FUNC
**ORIGIN:** sequence json-storage: else write fails

**STATEMENT:** A `persist task` call whose store-file write fails SHALL surface a storage error to `tasks` and SHALL leave the previously stored Tasks intact.

**RATIONALE:** Feature-level realization of REQ-ARCH-021 for the write-failure branch; the atomic replacement of REQ-FUNC-004 is only worth having if a failed write is observable and non-destructive.

**ACCEPTANCE_CRITERIA:**

1. Given the store-file write fails, When `storage` handles the failure, Then `storage` returns a storage error to `tasks` and no Task identifier.
2. Given a `persist task` call whose write failed, When the store file is read afterwards, Then it holds exactly the Tasks stored before that call.
3. Given a creation failure caused by a failed write, When `cli` renders it, Then the User receives an explicit error message and no confirmation.

**SOURCE_DIAGRAM:** docs/design/diagrams/json-storage.sequence.mmd
