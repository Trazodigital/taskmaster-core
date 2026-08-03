# 0002 — in process scheduler

## CONTEXT

REQ-ARCH-003 and REQ-ARCH-016 require a trigger that drives Due Date evaluation. The frozen flowchart places `scheduler` inside the system boundary. The alternative considered during diagram approval was letting `cli` evaluate Due Dates on each invocation, which would have made `notifications` a print statement inside the list-tasks path rather than an independent module.

## DECISION

Drive Due Date evaluation from an in-process `scheduler` module that ticks on an interval and depends on a `clock` port.

## RATIONALE

Reminders must reach the User independently of whether the User is running a command; that independence is what makes `notifications` a module at all. Depending on a `clock` port rather than reading the system time directly keeps due-date logic deterministic under test, which strict TDD requires.

## ALTERNATIVES

- Evaluate Due Dates inside each `cli` invocation — rejected: Reminders would only ever appear while the User was already looking, collapsing `notifications` into the list path.
- System cron / systemd timer — rejected: pushes scheduling into host configuration the product cannot test or ship.
- Background OS daemon — rejected: disproportionate operational weight for a single-user CLI.

## CONSEQUENCES

### POSITIVE

- `notifications` stays an independently testable module with its own port.
- A fake `clock` makes every Due Date test deterministic with no sleeping.
- The tick acknowledgement of REQ-ARCH-029 gives the scheduler a completion signal that is observable in tests.

### NEGATIVE

- Reminders only fire while a host process is alive; there is no delivery guarantee when nothing is running.
- Introduces a timing dimension to integration tests that a purely command-driven design would not have.

## STATUS

Accepted

## RELATED_REQS

- REQ-ARCH-003
- REQ-ARCH-016
- REQ-ARCH-029
- REQ-NFR-PERF-001
