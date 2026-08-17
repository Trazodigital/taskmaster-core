# 0001 — State lives in the ui block, the store is a backup

## CONTEXT

Taskmaster holds a small, single-user task list. Something has to own the authoritative in-memory
copy of that list and the currently active filter, and every other block has to be defined in terms
of not owning it. A component flowchart carries blocks and information flows; it has no notation for
"this block owns the state". Left unstated, each reader infers a different owner — the failure that
produced three contradictory data models in this product's previous architecture.

## DECISION

The `taskmaster-app` block holds the complete task list and the active filter in memory, and the
store is a backup that is read once at startup and written on every change, never read to render.

## RATIONALE

The list is small enough to hold entirely in memory, which removes any need to query the store
during a render and keeps the render path free of I/O. Concentrating state in one block makes
`task-model` a set of pure functions — the property that lets the domain be tested without a screen
or a disk, which the project's strict-TDD rule turns from a preference into a daily cost. It also
gives the composition root a single place to wire a concrete adapter, satisfying the
ports-and-adapters invariant the framework enforces.

## ALTERNATIVES

- **State in the domain (`task-model`)** — rejected: the filters would stop being pure, so every
  filter test would need a populated store.
- **State in the store, queried per render** — rejected: reintroduces I/O on the render path and
  makes an embedded database necessary for something that fits in memory.
- **State split across blocks** — rejected: the ownership question would have no single answer,
  which is precisely the failure this decision exists to prevent.

## CONSEQUENCES

### POSITIVE

- The render path performs no I/O.
- `task-model` is pure and testable with no fixtures.
- Exactly one block instantiates a concrete adapter.

### NEGATIVE

- Startup cost grows with the size of the store; bounded by `REQ-NFR-PERF-001`.
- Two application instances sharing one store each hold a stale copy, which is why external-change
  detection is required — see ADR 0003.

## STATUS

Accepted

## RELATED_REQS

- REQ-ARCH-001
- REQ-ARCH-013
- REQ-NFR-PERF-001
