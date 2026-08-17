# 0002 — A JSON file store, not an embedded database

## CONTEXT

Task records have to survive between runs on a single machine, for a single user, with no network.
The candidates were a server database, an embedded single-file database, and a plain text file.
Because ADR 0001 loads the whole list into memory and filters it with pure functions, no query is
ever issued against the store — which removes the reason most storage engines exist.

## DECISION

Task records are persisted in a single local JSON file, read once at startup and rewritten in full
on every change.

## RATIONALE

An embedded database earns its keep when data must be queried without being fully loaded, when
writers are concurrent, or when partial updates matter. None of those apply here, so it would add a
schema, migrations, and a query language while never being queried. A plain JSON file introduces no
new concept, is diffable, and can be inspected and repaired by hand — which matters for a personal
tool whose owner is also its operator. Its two real weaknesses, torn writes and hand-editing damage,
are addressed by ADR 0003 and by `REQ-ARCH-018` and `REQ-ARCH-021` rather than by a storage engine.

## ALTERNATIVES

- **PostgreSQL or another server database** — rejected: a separate always-running process, plus
  installation and credentials, for a personal task list.
- **SQLite** — rejected after the architecture was drawn: it is a single file and needs no server,
  but its advantages are querying without loading and crash-safe partial writes, and ADR 0001 gives
  up the first by design while `REQ-ARCH-021` obtains the second with a rename.
- **A bespoke binary format** — rejected: gives up hand-inspection and hand-repair for a size saving
  that is irrelevant at this scale.

## CONSEQUENCES

### POSITIVE

- No schema, no migrations, no query language, no new dependency.
- The store can be read, diffed, and repaired with any text editor.
- Adding a field later needs a default value, not a migration.

### NEGATIVE

- The whole file is rewritten on every change; acceptable at human editing speed and bounded by
  `REQ-NFR-PERF-001`.
- A file that a human can edit is a file a human can corrupt, which is why `REQ-ARCH-018` refuses to
  overwrite content it cannot parse.

## STATUS

Accepted

## RELATED_REQS

- REQ-ARCH-004
- REQ-ARCH-005
- REQ-ARCH-018
