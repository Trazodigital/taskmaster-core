# 0006 — Logs are written to a file, never to the terminal

## CONTEXT

The framework requires every feature to emit a `start` / `end` / `error` event triple, enforced on
the feature track by `check-traceability.sh --check-logging`. Taskmaster is a terminal user
interface, so the terminal is not a spare output channel — it is the application's own drawing
surface. Anything written to standard output or standard error lands on top of the interface and
corrupts it. This constraint is imposed by the chosen kind of application, binds every feature built
later, and cannot be expressed in a component flowchart or a sequence diagram, so it would otherwise
be rediscovered once per feature.

## DECISION

All structured log events are written to a log file; no code path writes log output to standard
output or standard error while the interface is running.

## RATIONALE

A terminal interface owns the screen for its whole run, so the usual default of logging to the
console is not merely untidy here, it breaks the product. A file is the only sink available without
adding a dependency or a running process, and it keeps logs readable after the fact — which is the
case that matters for a personal tool, where the person reading the log is the person who hit the
bug. Recording it once at architecture level rather than per feature also means the constraint is
stated where `structured-logging` can find it when it instruments each entry point.

## ALTERNATIVES

- **Standard output or standard error** — rejected: paints over the interface, which is the product.
- **No logging at all** — rejected: a failed save would leave no trace, and the framework gates
  feature verification on the event triple regardless.
- **An external log collector or logging service** — rejected: adds a dependency and a running
  process to an application that deliberately has neither, for a single-user local tool.

## CONSEQUENCES

### POSITIVE

- The interface is never corrupted by diagnostic output.
- Failures that happen off-screen, notably in the persistence path, leave a durable trace.
- Every feature inherits the constraint instead of rediscovering it.

### NEGATIVE

- Log output is not visible while the application runs; diagnosing means opening another terminal.
- The log file is one more file on disk whose location and growth have to be decided when the first
  feature is implemented.

## STATUS

Accepted

## RELATED_REQS

- REQ-ARCH-001
- REQ-ARCH-013
