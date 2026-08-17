# Date-view feature requirements

Feature-level requirement for tagging a task with a due date and viewing it by that date, derived
from the approved feature sequence diagram at `docs/design/diagrams/date-view.sequence.mmd`.
Fulfils the due-date and overdue halves of `REQ-ARCH-002`'s pure-filter contract for the first
time — space was the only dimension exercised until now (`REQ-FUNC-004`).

A task's due date is set through the same single text input `add-task` already uses: a trailing
`!<ISO date>` token (e.g. `!2026-08-20`) is parsed out and stored as the task's due date, leaving
the rest as its text and space. No new input widget. Per `docs/glossary.md § filter`, the date view
combines with the active space filter rather than replacing it — both narrow the same task list.

Per `docs/adr/0004-the-reference-date-is-injected-into-the-filters.md`, every date-sensitive filter
in `task-model` takes the reference date as an argument from `taskmaster-app`; none reads a system
clock.

---

## REQ-FUNC-005 — view tasks by due date

REFINES: REQ-ARCH-001, REQ-ARCH-002, REQ-ARCH-006, REQ-ARCH-007

SOURCE_DIAGRAM: docs/design/diagrams/date-view.sequence.mmd

STATEMENT: The user SHALL be able to tag a task with a due date via the existing add-task input and cycle taskmaster-app through views of tasks due today, due this week, and overdue.

RATIONALE: Due date and overdue were declared in the architecture from the start (REQ-ARCH-002) but nothing has captured or filtered on either — this is the last of the three filter dimensions the architecture promised, after space (REQ-FUNC-004).

ACCEPTANCE_CRITERIA:

- Given the user enters "send the invoice !2026-08-20" through the add-task input, When task-model builds the task record, Then its text is "send the invoice" and its due date is 2026-08-20.
- Given the user enters text with no trailing "!<date>", When task-model builds the task record, Then its due date is absent.
- Given taskmaster-app is running, When the user presses the cycle-date-view key, Then it advances through today, due this week, overdue, and back to no date view, supplying the current date to task-model on each filtered render rather than reading a clock itself.
- Given the due-today view is active, When task-model filters the full task list, Then it returns only incomplete tasks whose due date equals the supplied current date.
- Given the due-this-week view is active, When task-model filters the full task list, Then it returns only tasks matching docs/glossary.md's definition of "due this week" for the supplied current date.
- Given the overdue view is active, When task-model filters the full task list, Then it returns only tasks matching docs/glossary.md's definition of "overdue" for the supplied current date.
- Given both an active space and an active date view, When taskmaster-app renders the list, Then it shows only tasks satisfying both, per docs/glossary.md's definition of "filter".
- Given identical inputs, When a date filter is invoked twice, Then both invocations return the same result.
