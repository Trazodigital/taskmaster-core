# REQ-FUNC-005

**TYPE:** FUNC
**ORIGIN:** sequence json-storage: alt stored content is not valid json

**STATEMENT:** A `persist task` call against a store file whose content is not valid JSON SHALL fail with an explicit storage error and SHALL NOT overwrite that file.

**RATIONALE:** Feature-level realization of REQ-ARCH-021 for the corrupt-store branch; overwriting an unreadable store would destroy Tasks the User never asked to delete.

**ACCEPTANCE_CRITERIA:**

1. Given the store file content is not valid JSON, When `storage` reads it during a `persist task` call, Then `storage` returns a storage error to `tasks` and `tasks` returns a creation failure to `cli`.
2. Given a store file whose content is not valid JSON, When the `persist task` call fails, Then the file content is unchanged byte for byte.
3. Given a creation failure caused by an unreadable store file, When `cli` renders it, Then the User receives an explicit error message and no confirmation.

**SOURCE_DIAGRAM:** docs/design/diagrams/json-storage.sequence.mmd
