# Selection-lost-on-refresh bugfix design

## SUMMARY

Fixes a defect against `REQ-FUNC-002`/`REQ-FUNC-003`'s already-approved acceptance criteria: toggling
or deleting the selected task must act on the task the user selected. As shipped, `_refresh_list`
always calls `ListView.clear()`, which drops the list's selection unconditionally; the fallback
`if task_list.index is None: task_list.index = 0` (added to fix an earlier reachability defect —
nothing was selected right after adding the very first task) cannot tell that apart from "a
selection just got wiped by this same refresh." Every refresh — including the one `_act_on_selected`
itself triggers right after acting on the selected task — resets the selection to index 0. Confirmed
live: with two tasks visible, selecting the second and pressing the toggle key once flips it
correctly, but the refresh that follows silently re-selects the first task; a second press flips the
*first* task, not the second one back off.

The fix: `_refresh_list` captures the list's current index before clearing it, and restores that same
position afterward (clamped to the new list's length) instead of always defaulting to 0. It only
falls back to 0 when there truly was no prior selection — the original reachability case this
fallback was written for.

No new architectural surface. Corrective, not additive — `REQ-FUNC-002`/`REQ-FUNC-003` already
require acting on "the selected task"; this fixes what stays selected across the render they both
already trigger.

## REQS_COVERED

- REQ-FUNC-002
- REQ-FUNC-003

## MODULES

- **ui** — corrects `_refresh_list`'s own selection-preservation responsibility.

## PORTS

> None. Selection is UI-internal `ListView` state; no port is touched.

## ADAPTERS

> None. No adapter changes.

## DATA_FLOW

1. `ui` (self) — before clearing the list, the currently selected position is captured.
2. `ui` (self) — after rebuilding the list, that same position is restored if still in range; otherwise (or if nothing was selected before) the first task is selected, exactly as the original reachability fix intended.

## DIAGRAMS

<!-- source: docs/design/diagrams/selection-lost-on-refresh.sequence.mmd -->

```mermaid
sequenceDiagram
    actor user
    box ui
    participant app as taskmaster-app
    end

    Note over app: two tasks are visible; the user has selected the second one

    user->>app: space, to toggle the selected task
    app->>app: toggle the second task, then clear and rebuild the list
    app->>app: selection was lost by clear(), so it resets to the first task instead of staying on the second

    user->>app: space again, expecting to toggle the second task back off
    app->>app: toggles the first task instead — the wrong one
```

## DECISIONS

None. No new dependency, no port change; corrects an implementation defect against already-approved
requirements rather than introducing a new architectural decision.

## SECURITY_TEST_PLAN

> No port is touched by this fix. Nothing about what data crosses any boundary changes — only which
> list position the app treats as selected after a render.
