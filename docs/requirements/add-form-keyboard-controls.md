# Add-form-keyboard-controls feature requirements

Feature-level requirement for canceling the add form, derived from the approved feature sequence
diagram at `docs/design/diagrams/add-form-keyboard-controls.sequence.mmd`. Tab/Shift+Tab already
cycle the three fields (REQ-FUNC-006) and are unchanged by this feature.

---

## REQ-FUNC-010 — cancel the add form with escape

REFINES: REQ-ARCH-001

SOURCE_DIAGRAM: docs/design/diagrams/add-form-keyboard-controls.sequence.mmd

STATEMENT: taskmaster-app SHALL, when the user presses escape while any of the add form's three fields has focus, clear the text and space fields, reset the date field to the current date, and return focus to the task list without creating a task.

RATIONALE: Today the only way out of a partially-filled add form is to finish it — pressing enter with an empty text field silently does nothing, but the space and date fields keep whatever was typed or stepped into them, and Textual doesn't otherwise clear a field just by leaving it. Escape gives an explicit, immediate way to abandon what's typed and get back to the list.

ACCEPTANCE_CRITERIA:

- Given the text field has focus with any text typed, When the user presses escape, Then no task is created and the text field is empty.
- Given the space field has focus with a value typed, When the user presses escape, Then the space field is empty.
- Given the date field has focus showing a date other than today, When the user presses escape, Then the date field shows the current date again.
- Given escape is pressed on any of the three fields, When the app responds, Then focus returns to the task list.
