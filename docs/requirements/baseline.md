# Baseline architecture requirements

System-level requirements for Taskmaster, derived from the two approved spec-level diagrams under
`docs/architecture/diagrams/`. Structural requirements come from the component flowchart; behavioral
requirements come from the sequence diagram.

`ARCH` is a root type in `requirements-tracker.yaml § relations.refines.roots`, so no entry here
declares a `REFINES:` parent.

---

## REQ-ARCH-001 — taskmaster-app block

DERIVED_FROM: node

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

SOURCE_DIAGRAM_SEQUENCE: docs/architecture/diagrams/baseline.sequence.mmd

STATEMENT: The system SHALL provide a taskmaster-app block that holds the complete task list and the active filter in memory, translates user input into actions, and is the only block that instantiates a concrete adapter.

ACCEPTANCE_CRITERIA:

- Given the application has started, When any block other than taskmaster-app is inspected, Then none of them holds the complete task list or the active filter.
- Given the application is running, When the source is inspected for the name of a concrete adapter, Then that name appears only inside taskmaster-app.
- Given a rendered view, When taskmaster-app supplies data to a widget, Then the widget receives an already-filtered task list and performs no selection of its own.

---

## REQ-ARCH-002 — task-model block

DERIVED_FROM: node

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: The system SHALL provide a task-model block that defines the task record shape and the pure filters selecting tasks by space, by due date, and by overdue state.

ACCEPTANCE_CRITERIA:

- Given a task list and a filter, When task-model is invoked, Then it returns a task list and performs no read or write of stored data.
- Given identical inputs, When a filter in task-model is invoked twice, Then both invocations return the same result.
- Given an overdue filter, When it is invoked, Then the reference date is supplied by the caller rather than read from a system clock inside the filter.

---

## REQ-ARCH-003 — TaskRepository port

DERIVED_FROM: node

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: The system SHALL provide a TaskRepository port declaring the load and save operations required to persist task records, without declaring any storage technology.

ACCEPTANCE_CRITERIA:

- Given the TaskRepository declaration, When it is inspected, Then it names no file format, path, or storage product.
- Given the TaskRepository declaration, When its load operation is inspected, Then it returns both the stored task records and a file fingerprint.
- Given the TaskRepository declaration, When its save operation is inspected, Then it accepts both the task list and the file fingerprint held by the caller.

---

## REQ-ARCH-004 — JsonFileRepository adapter

DERIVED_FROM: node

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: The system SHALL provide a JsonFileRepository block that implements TaskRepository against a local JSON file and is the only block aware that the store is a JSON file.

ACCEPTANCE_CRITERIA:

- Given the whole source tree, When it is searched for JSON serialisation of task records, Then every occurrence is inside JsonFileRepository.
- Given the whole source tree, When it is searched for the store's filesystem path, Then that path is referenced only by JsonFileRepository.
- Given TaskRepository, When its adapters are enumerated, Then JsonFileRepository is present with a real runtime and at least one test-double adapter is present alongside it.

---

## REQ-ARCH-005 — tasks.json store

DERIVED_FROM: node

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: The system SHALL persist task records in a single local JSON file that outlives any run of the application and belongs to no module.

ACCEPTANCE_CRITERIA:

- Given the application has exited, When the store path is inspected, Then the task records written during the run are still present.
- Given the module directories under src, When they are inspected, Then none of them contains the store file.
- Given a running application, When the store is examined, Then exactly one store file is in use.

---

## REQ-ARCH-006 — task list and active filter flow

DERIVED_FROM: edge

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: Information "task list and active filter" SHALL flow from taskmaster-app to task-model whenever a view is rendered.

ACCEPTANCE_CRITERIA:

- Given a render is due, When taskmaster-app calls task-model, Then it passes the complete task list, the active filter, and the current date.
- Given that call, When task-model is inspected, Then it obtained the task list from its arguments and from no other source.

---

## REQ-ARCH-007 — filtered task list flow

DERIVED_FROM: edge

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: Information "filtered task list" SHALL flow from task-model back to taskmaster-app as the direct result of every filter invocation.

ACCEPTANCE_CRITERIA:

- Given a task list and an active filter, When task-model returns, Then the returned list contains only tasks satisfying that filter.
- Given the returned list, When it is compared with the input list, Then no task has been altered, only selected.

---

## REQ-ARCH-008 — load and save requests flow to the port

DERIVED_FROM: edge

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: Information "load and save requests" SHALL flow from taskmaster-app to TaskRepository at startup and on every change to a task.

ACCEPTANCE_CRITERIA:

- Given the application starts, When it reaches its first render, Then exactly one load request has been sent to TaskRepository.
- Given a task is added, completed, edited, or deleted, When the change is applied in memory, Then one save request is sent to TaskRepository.
- Given any request, When it is inspected, Then it was issued by taskmaster-app and by no other block.

---

## REQ-ARCH-009 — load and save outcomes flow from the port

DERIVED_FROM: edge

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: Information "load and save outcomes" SHALL flow from TaskRepository back to taskmaster-app for every request it received.

ACCEPTANCE_CRITERIA:

- Given a load request, When TaskRepository responds, Then the response is either the stored task records with a file fingerprint, an empty task list, or an unreadable-store error.
- Given a save request, When TaskRepository responds, Then the response is either a confirmation with a new file fingerprint or an external-change report.
- Given any request, When TaskRepository has finished, Then exactly one outcome has been returned to taskmaster-app.

---

## REQ-ARCH-010 — load and save requests reach the adapter

DERIVED_FROM: edge

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: Information "load and save requests" SHALL flow from TaskRepository to the adapter bound to it, unchanged in content.

ACCEPTANCE_CRITERIA:

- Given a request sent through TaskRepository, When the bound adapter receives it, Then the task list and file fingerprint it receives are identical to those supplied by taskmaster-app.
- Given a bound test-double adapter, When the same request is sent, Then taskmaster-app requires no modification for it to be served.

---

## REQ-ARCH-011 — task records to persist flow

DERIVED_FROM: edge

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: Information "task records to persist" SHALL flow from JsonFileRepository to the store only after the file fingerprint check has passed.

ACCEPTANCE_CRITERIA:

- Given a save request, When the fingerprint check has not yet run, Then no write to the store has occurred.
- Given a failed fingerprint check, When the save request completes, Then the store is byte-for-byte unchanged.

---

## REQ-ARCH-012 — stored task records flow

DERIVED_FROM: edge

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: Information "stored task records" SHALL flow from the store to JsonFileRepository only during a load, and never during a render.

ACCEPTANCE_CRITERIA:

- Given the application is running, When a view is rendered, Then the store is not read.
- Given a load, When JsonFileRepository reads the store, Then it also derives the file fingerprint from what it read.

---

## REQ-ARCH-013 — ui module boundary

DERIVED_FROM: subgraph

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: The ui boundary SHALL contain exactly the taskmaster-app block and expose only its exchanges with task-model and TaskRepository.

ACCEPTANCE_CRITERIA:

- Given the ui module directory, When its contents are enumerated, Then they implement taskmaster-app and nothing else.
- Given any block outside ui, When it is inspected, Then it references no terminal, screen, widget, or key binding.

---

## REQ-ARCH-014 — tasks module boundary

DERIVED_FROM: subgraph

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: The tasks boundary SHALL contain exactly the task-model block and the TaskRepository port, and expose only its exchanges with taskmaster-app and the bound adapter.

ACCEPTANCE_CRITERIA:

- Given the tasks module directory, When its contents are enumerated, Then they implement the task record shape, the pure filters, and the TaskRepository declaration, and nothing else.
- Given the tasks module, When its dependencies are inspected, Then it depends on no storage implementation and on no user-interface library.

---

## REQ-ARCH-015 — storage module boundary

DERIVED_FROM: subgraph

SOURCE_DIAGRAM_FLOWCHART: docs/architecture/diagrams/baseline.flowchart.mmd

STATEMENT: The storage boundary SHALL contain exactly the adapters implementing TaskRepository and expose only that port and its exchanges with the store.

ACCEPTANCE_CRITERIA:

- Given the storage module directory, When its contents are enumerated, Then every unit in it implements TaskRepository.
- Given the storage module, When its dependencies are inspected, Then it depends on the tasks module and on no user-interface library.

---

## REQ-ARCH-016 — the store is read once, before the first render

DERIVED_FROM: invariant

SOURCE_DIAGRAM_SEQUENCE: docs/architecture/diagrams/baseline.sequence.mmd

STATEMENT: The store SHALL be read exactly once per run, at startup, before the first view is rendered.

ACCEPTANCE_CRITERIA:

- Given a run of the application, When the first view is rendered, Then the load has already completed.
- Given a run in which many views are rendered, When store reads are counted, Then the count is exactly one.

---

## REQ-ARCH-017 — an absent store yields an empty task list

DERIVED_FROM: invariant

SOURCE_DIAGRAM_SEQUENCE: docs/architecture/diagrams/baseline.sequence.mmd

STATEMENT: When no store file exists, loading SHALL yield an empty task list and an absent file fingerprint rather than an error.

ACCEPTANCE_CRITERIA:

- Given no store file exists, When the application starts, Then it starts successfully and presents an empty task list.
- Given that first run, When the user has made no change, Then no store file has been created.

---

## REQ-ARCH-018 — unreadable stored content is never overwritten

DERIVED_FROM: invariant

SOURCE_DIAGRAM_SEQUENCE: docs/architecture/diagrams/baseline.sequence.mmd

STATEMENT: When a store file exists but its content cannot be parsed, the application SHALL report the error and stop without writing to the store.

ACCEPTANCE_CRITERIA:

- Given a store file whose content is not parseable, When the application starts, Then it reports an unreadable-store error and does not present a task list.
- Given that same run, When the store is compared byte-for-byte with its state before the run, Then it is unchanged.
- Given unreadable stored content, When the load path is inspected, Then it is distinguishable from the absent-store path and does not share its empty-list outcome.

---

## REQ-ARCH-019 — the file fingerprint is checked before every write

DERIVED_FROM: invariant

SOURCE_DIAGRAM_SEQUENCE: docs/architecture/diagrams/baseline.sequence.mmd

STATEMENT: Every save SHALL compare the file fingerprint held by the caller against the store's current fingerprint before any write occurs.

ACCEPTANCE_CRITERIA:

- Given a save request, When the write path is traced, Then the fingerprint comparison precedes every write operation.
- Given a successful save, When it completes, Then a new file fingerprint is returned to the caller for use in the next save.

---

## REQ-ARCH-020 — an externally changed store is never overwritten

DERIVED_FROM: invariant

SOURCE_DIAGRAM_SEQUENCE: docs/architecture/diagrams/baseline.sequence.mmd

STATEMENT: When the store's current fingerprint differs from the one held by the caller, the save SHALL write nothing and report the external change.

ACCEPTANCE_CRITERIA:

- Given the store was modified after it was loaded, When a save is attempted, Then nothing is written and an external-change report is returned.
- Given that report, When the store is compared byte-for-byte with its state before the save, Then it is unchanged.
- Given an external change, When the outcome is inspected, Then no attempt is made to merge the two versions.

---

## REQ-ARCH-021 — writes reach the store by rename, never in place

DERIVED_FROM: invariant

SOURCE_DIAGRAM_SEQUENCE: docs/architecture/diagrams/baseline.sequence.mmd

STATEMENT: Task records SHALL be written to a temporary file and then renamed over the store, so that an interrupted write leaves the previous content intact.

ACCEPTANCE_CRITERIA:

- Given a save, When the write path is traced, Then the store is modified only by a rename and never by an in-place write.
- Given a write interrupted before the rename, When the store is read afterwards, Then it still holds the content it had before the save began.
- Given the temporary file, When its location is inspected, Then it is on the same filesystem as the store so the rename is atomic.

---

## REQ-NFR-PERF-001 — startup stays imperceptible at the declared corpus size

REFINES: REQ-ARCH-016

STATEMENT: The application SHALL complete its startup load and present the first view within a bounded time when the store holds one thousand tasks.

METRIC: cold start time to first rendered view

THRESHOLD: <= 200ms

MEASUREMENT_METHOD:
  INSTRUMENT: suites.bench
  WINDOW: per-release
  SAMPLE: >= 20 consecutive runs against a store holding 1000 tasks

ACCEPTANCE_CRITERIA:

- Given a store holding one thousand tasks, When the application is started, Then the first view is presented within the declared threshold.
- Given the benchmark suite, When it runs, Then it reports the cold start metric so the threshold can be compared without human interpretation.
- Given a change that makes startup exceed the threshold, When the benchmark suite runs, Then it reports the regression rather than passing silently.
