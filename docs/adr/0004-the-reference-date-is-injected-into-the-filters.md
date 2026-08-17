# 0004 — The reference date is injected into the filters

## CONTEXT

Two of the filters in `task-model` — the due-date view and the overdue view — compare a task's due
date against "now". Where that "now" comes from decides whether the filters are pure functions. A
filter that reads a system clock internally produces a different answer on a different day from the
same input, so its test passes today and fails next week. The project's strict-TDD rule makes that a
recurring cost rather than a one-off annoyance.

## DECISION

The reference date is passed into every date-sensitive filter as an argument by `taskmaster-app`,
and no filter in `task-model` reads a clock.

## RATIONALE

Passing the date preserves the property that makes the domain cheap to test: identical inputs give
identical outputs, with no screen, no disk, and no date faking. It also puts the one piece of
ambient state the domain would otherwise depend on under the control of the block that already owns
all state per ADR 0001, which keeps the ownership rule uniform. Modelling the clock as a port with a
real adapter and a test double would buy the same determinism, but at the cost of an extra module
directory with its own mandatory test folder — the framework's module-as-directory rule makes that a
real, permanent structural cost for a value that is one argument wide.

## ALTERNATIVES

- **Read the clock inside the filter** — rejected: destroys purity and makes every date test
  time-dependent.
- **A `Clock` port with real and test-double adapters** — rejected: correct but disproportionate; it
  adds a declared module, a directory, and a mandatory test folder to inject one value.
- **Freeze the date globally at startup** — rejected: a long-running session would silently keep
  yesterday's notion of "today", so a task would never become overdue while the app stays open.

## CONSEQUENCES

### POSITIVE

- Every date-sensitive filter is deterministic and testable without patching time.
- The domain depends on no ambient state at all.

### NEGATIVE

- Every call site must supply the date, so forgetting it is a possible mistake; it is caught at the
  call boundary rather than by a gate.
- `taskmaster-app` acquires one more responsibility, on a block that already carries several.

## STATUS

Accepted

## RELATED_REQS

- REQ-ARCH-002
- REQ-ARCH-006
