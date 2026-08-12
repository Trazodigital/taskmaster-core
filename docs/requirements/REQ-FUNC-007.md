# REQ-FUNC-007

**TYPE:** FUNC
**ORIGIN:** sequence json-storage: Startup block and Durability block

**STATEMENT:** `app` SHALL construct the JSON-file task-repository with the store path at startup, so a Task persisted in one run is returned by a `list tasks` Command in the next run.

**RATIONALE:** Closes the composition-root and entrypoint debt left by REQ-FUNC-001; durability across processes is only observable end to end once a real entrypoint wires the real adapter.

**ACCEPTANCE_CRITERIA:**

1. Given the User runs the taskmaster command, When `app` starts, Then `app` constructs the JSON-file task-repository with the store path and hands the wired command-input and task-repository to `cli`, and no other module constructs an adapter.
2. Given a Task persisted in one run, When the command runs again against the same store path and the User issues a `list tasks` Command, Then `tasks` loads the stored Tasks and `cli` renders a Task List containing that Task.
3. Given a store path whose file does not exist, When the User issues a `list tasks` Command, Then `cli` renders an empty Task List and the User receives no error.

**SOURCE_DIAGRAM:** docs/design/diagrams/json-storage.sequence.mmd
