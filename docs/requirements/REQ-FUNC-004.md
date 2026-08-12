# REQ-FUNC-004

**TYPE:** FUNC
**ORIGIN:** sequence json-storage: alt store file absent / else store file present, alt write succeeds

**STATEMENT:** A `persist task` call SHALL append the Task to the JSON store file and replace that file atomically, returning the persisted Task identifier.

**RATIONALE:** Durable persistence of Tasks in JSON files on disk, realizing the `JsonFileTaskRepository` adapter declared by the architecture so a Task survives the process that created it.

**ACCEPTANCE_CRITERIA:**

1. Given the store file does not exist, When `storage` receives a `persist task` call, Then `storage` treats the run as an empty store and the resulting file holds exactly the new Task.
2. Given the store file exists and holds valid JSON, When `storage` receives a `persist task` call, Then `storage` reads the whole file, appends the Task with an assigned identifier, and returns that identifier to `tasks`.
3. Given a `persist task` call that succeeds, When the store file is written, Then the write is an atomic replacement, so no reader observes a partially written store file.

**SOURCE_DIAGRAM:** docs/design/diagrams/json-storage.sequence.mmd
