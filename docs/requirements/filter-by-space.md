# Filter-by-space feature requirements

Feature-level requirement for tagging a task with a space and viewing only one space at a time,
derived from the approved feature sequence diagram at
`docs/design/diagrams/filter-by-space.sequence.mmd`. Fulfils the space-filtering half of
`REQ-ARCH-002`'s contract ("the pure filters selecting tasks by space, by due date, and by overdue
state") for the first time — no prior feature has exercised it.

A task's space is set through the same single text input `add-task` already uses: trailing
`@<space>` in the entered text is parsed out and stored as the task's space, leaving the rest as
its text. No new input widget. Tasks entered without a trailing `@<space>` keep an empty space,
consistent with `docs/glossary.md`'s definition of space existing only while a task names it.

---

## REQ-FUNC-004 — filter the task list by space

REFINES: REQ-ARCH-001, REQ-ARCH-002, REQ-ARCH-006, REQ-ARCH-007

SOURCE_DIAGRAM: docs/design/diagrams/filter-by-space.sequence.mmd

STATEMENT: The user SHALL be able to tag a task with a space via the existing add-task input and view only the tasks in one space at a time through taskmaster-app.

RATIONALE: Space was declared in the architecture from the start (REQ-ARCH-002) but nothing has captured or filtered on it yet — every task has lived in one flat, unfiltered list. This is the smallest change that exercises that half of the architecture's contract for the first time.

ACCEPTANCE_CRITERIA:

- Given the user enters "buy bread @work" through the add-task input, When task-model builds the task record, Then its text is "buy bread" and its space is "work".
- Given the user enters "buy bread" with no trailing "@<space>", When task-model builds the task record, Then its space is empty.
- Given taskmaster-app is running with tasks in more than one space, When the user presses the cycle-filter key, Then task-model reports the distinct spaces present in the full task list and taskmaster-app advances to the next one in that set, wrapping to showing every task after the last one.
- Given an active space filter, When task-model filters the full task list by it, Then it returns only the tasks whose space matches, performing no read or write of stored data.
- Given identical inputs, When the space filter is invoked twice, Then both invocations return the same result.
