# REQ-FUNC-001

**TYPE:** FUNC
**ORIGIN:** sequence create-task: alt title present / alt persisted

**STATEMENT:** A `create task` Command carrying a title SHALL persist a new Task through `storage` and return a confirmation carrying the persisted Task identifier.

**RATIONALE:** Allow the User to create a Task from the command line; this is the first Task lifecycle operation the product exposes.

**ACCEPTANCE_CRITERIA:**

1. Given the User issues a `create task` Command carrying a title, When `cli` parses the command arguments, Then `cli` obtains a parsed create-task Command and forwards it to `tasks`.
2. Given `tasks` receives a parsed create-task Command, When `tasks` persists the Task through `storage`, Then `storage` returns the persisted Task identifier.
3. Given `storage` returns the persisted Task identifier, When `cli` renders the result, Then the User receives a confirmation carrying that identifier.

**SOURCE_DIAGRAM:** docs/design/diagrams/create-task.sequence.mmd
