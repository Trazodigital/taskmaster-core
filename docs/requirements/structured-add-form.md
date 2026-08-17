# Structured-add-form feature requirements

Feature-level requirement for capturing a task's space and due date through dedicated form fields,
derived from the approved feature sequence diagram at
`docs/design/diagrams/structured-add-form.sequence.mmd`. Replaces the inline `@<space>`/`!<date>`
text-tag entry `REQ-FUNC-004`/`REQ-FUNC-005` established with three dedicated fields: text, space,
and a date field pre-filled with the current date and adjustable a day at a time.

`task-model`'s existing `new_task` parser (`REQ-FUNC-004`, `REQ-FUNC-005`) is unchanged and keeps
passing its own tests; this feature simply stops calling it from the live add-task flow, building
the task record from the three already-distinct field values instead.

---

## REQ-FUNC-006 — capture space and due date through dedicated form fields

REFINES: REQ-ARCH-001, REQ-ARCH-002, REQ-ARCH-006, REQ-ARCH-007

SOURCE_DIAGRAM: docs/design/diagrams/structured-add-form.sequence.mmd

STATEMENT: The user SHALL enter a task's text, space, and due date through three dedicated fields when adding a task, with the date field pre-filled to the current date and adjustable a day at a time via the up and down keys.

RATIONALE: Typing "@work" and "!2026-08-20" by hand is precise but easy to forget the exact syntax for; a dedicated space field with a placeholder and a date field that already shows today and only needs adjusting removes the need to remember either.

ACCEPTANCE_CRITERIA:

- Given the user presses the add key, When the form opens, Then the date field already shows the current date, and the text and space fields are empty.
- Given the date field has focus, When the user presses the up key, Then the field advances by one day; When the user presses the down key, Then it moves back by one day.
- Given the user presses enter on any of the three fields, When the text field is non-empty, Then task-model builds a task record from the text field's text, the space field's value as its space, and the date field's value as its due date.
- Given the date field is empty at submission, When task-model builds the task record, Then its due date is absent rather than defaulting to any date.
- Given the date field holds text that does not parse as a date at submission, When task-model builds the task record, Then its due date is absent and the task is still created rather than the submission being blocked or the application crashing.
- Given a task was just created, When the form's fields are inspected, Then the text and space fields are empty and the date field again shows the current date.
