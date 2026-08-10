# REQ-FUNC-003

**TYPE:** FUNC
**ORIGIN:** sequence create-task: alt storage unavailable or write timed out

**STATEMENT:** A `create task` persist that fails or exceeds the 5-second timeout declared by REQ-ARCH-022 SHALL surface to the User as an explicit error and never as a confirmation.

**RATIONALE:** Feature-level realization of REQ-ARCH-021 for the create-task flow, so the silent-success failure mode is covered by an executable test rather than by the architecture invariant alone.

**ACCEPTANCE_CRITERIA:**

1. Given `storage` returns a storage error on persist, When `tasks` receives it, Then `tasks` returns a creation failure to `cli`.
2. Given the persist exceeds the 5-second timeout declared by REQ-ARCH-022, When `tasks` receives the timeout, Then `tasks` returns a creation failure to `cli` without retrying.
3. Given a creation failure, When `cli` renders it, Then the User receives an explicit error message and no confirmation.

**SOURCE_DIAGRAM:** docs/design/diagrams/create-task.sequence.mmd
