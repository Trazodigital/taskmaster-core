# Active-view-indicator feature requirements

Feature-level requirement for showing the currently active filter, derived from the approved
feature sequence diagram at `docs/design/diagrams/active-view-indicator.sequence.mmd`. Cycling the
space filter (`f`) and the date view (`v`) already changes what `visible_tasks` shows; this feature
makes the active choice visible instead of leaving the user to infer it from the task list alone.

---

## REQ-FUNC-008 — show the currently active filter

REFINES: REQ-ARCH-001

SOURCE_DIAGRAM: docs/design/diagrams/active-view-indicator.sequence.mmd

STATEMENT: taskmaster-app SHALL display the active space and the active date view components of the current filter, updated whenever either is cycled.

RATIONALE: Cycling through spaces and date views changes which tasks are visible with no on-screen confirmation of which one is now selected; a user has to remember how many times they pressed `f` or `v` to know their own filter, which the status line removes.

ACCEPTANCE_CRITERIA:

- Given no space filter is active, When the status line is inspected, Then it shows the space component as "all".
- Given the user presses the cycle-filter key, When the active space changes, Then the status line shows the new active space by name.
- Given no date view is active, When the status line is inspected, Then it shows the date-view component as "all".
- Given the user presses the cycle-date-view key, When the active date view changes, Then the status line shows the new active date view by name.
- Given both an active space and an active date view, When the status line is inspected, Then both components are shown together.
