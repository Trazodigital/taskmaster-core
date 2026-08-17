# Requirements overview

Every requirement in the corpus, grouped by the file it is authored in.
Generated from the corpus by `check-traceability.sh --report --overview` —
do not edit by hand.

## Active-view-indicator feature requirements

Source: `docs/requirements/active-view-indicator.md`

| UID | Derived from | Statement |
|---|---|---|
| REQ-FUNC-008 | invariant ? | taskmaster-app SHALL display the active space and the active date view components of the current filter, updated whenever either is cycled. |

## Add-task feature requirements

Source: `docs/requirements/add-task.md`

| UID | Derived from | Statement |
|---|---|---|
| REQ-FUNC-001 | invariant ? | The user SHALL be able to enter a task's text through taskmaster-app and have it added to the task list and persisted through TaskRepository. |

## Baseline architecture requirements

Source: `docs/requirements/baseline.md`

| UID | Derived from | Statement |
|---|---|---|
| REQ-ARCH-001 | node | The system SHALL provide a taskmaster-app block that holds the complete task list and the active filter in memory, translates user input into actions, and is the only block that instantiates a concrete adapter. |
| REQ-ARCH-002 | node | The system SHALL provide a task-model block that defines the task record shape and the pure filters selecting tasks by space, by due date, and by overdue state. |
| REQ-ARCH-003 | node | The system SHALL provide a TaskRepository port declaring the load and save operations required to persist task records, without declaring any storage technology. |
| REQ-ARCH-004 | node | The system SHALL provide a JsonFileRepository block that implements TaskRepository against a local JSON file and is the only block aware that the store is a JSON file. |
| REQ-ARCH-005 | node | The system SHALL persist task records in a single local JSON file that outlives any run of the application and belongs to no module. |
| REQ-ARCH-006 | edge | Information "task list and active filter" SHALL flow from taskmaster-app to task-model whenever a view is rendered. |
| REQ-ARCH-007 | edge | Information "filtered task list" SHALL flow from task-model back to taskmaster-app as the direct result of every filter invocation. |
| REQ-ARCH-008 | edge | Information "load and save requests" SHALL flow from taskmaster-app to TaskRepository at startup and on every change to a task. |
| REQ-ARCH-009 | edge | Information "load and save outcomes" SHALL flow from TaskRepository back to taskmaster-app for every request it received. |
| REQ-ARCH-010 | edge | Information "load and save requests" SHALL flow from TaskRepository to the adapter bound to it, unchanged in content. |
| REQ-ARCH-011 | edge | Information "task records to persist" SHALL flow from JsonFileRepository to the store only after the file fingerprint check has passed. |
| REQ-ARCH-012 | edge | Information "stored task records" SHALL flow from the store to JsonFileRepository only during a load, and never during a render. |
| REQ-ARCH-013 | subgraph | The ui boundary SHALL contain exactly the taskmaster-app block and expose only its exchanges with task-model and TaskRepository. |
| REQ-ARCH-014 | subgraph | The tasks boundary SHALL contain exactly the task-model block and the TaskRepository port, and expose only its exchanges with taskmaster-app and the bound adapter. |
| REQ-ARCH-015 | subgraph | The storage boundary SHALL contain exactly the adapters implementing TaskRepository and expose only that port and its exchanges with the store. |
| REQ-ARCH-016 | invariant | The store SHALL be read exactly once per run, at startup, before the first view is rendered. |
| REQ-ARCH-017 | invariant | When no store file exists, loading SHALL yield an empty task list and an absent file fingerprint rather than an error. |
| REQ-ARCH-018 | invariant | When a store file exists but its content cannot be parsed, the application SHALL report the error and stop without writing to the store. |
| REQ-ARCH-019 | invariant | Every save SHALL compare the file fingerprint held by the caller against the store's current fingerprint before any write occurs. |
| REQ-ARCH-020 | invariant | When the store's current fingerprint differs from the one held by the caller, the save SHALL write nothing and report the external change. |
| REQ-ARCH-021 | invariant | Task records SHALL be written to a temporary file and then renamed over the store, so that an interrupted write leaves the previous content intact. |
| REQ-NFR-PERF-001 | invariant ? | The application SHALL complete its startup load and present the first view within a bounded time when the store holds one thousand tasks. |

## Date-view feature requirements

Source: `docs/requirements/date-view.md`

| UID | Derived from | Statement |
|---|---|---|
| REQ-FUNC-005 | invariant ? | The user SHALL be able to tag a task with a due date via the existing add-task input and cycle taskmaster-app through views of tasks due today, due this week, and overdue. |

## Delete-task feature requirements

Source: `docs/requirements/delete-task.md`

| UID | Derived from | Statement |
|---|---|---|
| REQ-FUNC-003 | invariant ? | The user SHALL be able to remove an existing task through taskmaster-app and have the change persisted through TaskRepository. |

## Filter-by-space feature requirements

Source: `docs/requirements/filter-by-space.md`

| UID | Derived from | Statement |
|---|---|---|
| REQ-FUNC-004 | invariant ? | The user SHALL be able to tag a task with a space via the existing add-task input and view only the tasks in one space at a time through taskmaster-app. |

## Structured-add-form feature requirements

Source: `docs/requirements/structured-add-form.md`

| UID | Derived from | Statement |
|---|---|---|
| REQ-FUNC-006 | invariant ? | The user SHALL enter a task's text, space, and due date through three dedicated fields when adding a task, with the date field pre-filled to the current date and adjustable a day at a time via the up and down keys. |

## Toggle-task feature requirements

Source: `docs/requirements/toggle-task.md`

| UID | Derived from | Statement |
|---|---|---|
| REQ-FUNC-002 | invariant ? | The user SHALL be able to flip an existing task's done state through taskmaster-app and have the change persisted through TaskRepository. |

## Welcome-screen feature requirements

Source: `docs/requirements/welcome-screen.md`

| UID | Derived from | Statement |
|---|---|---|
| REQ-FUNC-007 | invariant ? | The application SHALL show a welcome screen carrying the ASCII banner and a static list of its key bindings before the task list on launch, dismissed by any keypress, and SHALL show it again on demand when the user presses the "?" key. |

---

30 requirement(s). `Derived from`: 21 declared, 9 inferred (marked `?`), 0 undetermined.

An inferred value was read from the statement's shape, not from the entry. Add a `DERIVED_FROM:` line to record it as fact.

