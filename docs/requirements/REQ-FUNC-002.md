# REQ-FUNC-002

**TYPE:** FUNC
**ORIGIN:** sequence create-task: alt title missing or blank

**STATEMENT:** A `create task` Command whose title is missing or blank SHALL be rejected before any persist is attempted.

**RATIONALE:** A Task with no title is not addressable by the User, so the rejection belongs at the trust boundary rather than in `storage`.

**ACCEPTANCE_CRITERIA:**

1. Given the User issues a `create task` Command whose title is missing or blank, When `cli` parses the command arguments, Then `cli` obtains a rejected command and the User receives a validation error message.
2. Given a rejected create-task Command, When `cli` handles it, Then `tasks` is never invoked and `storage` receives no persist call.

**SOURCE_DIAGRAM:** docs/design/diagrams/create-task.sequence.mmd
