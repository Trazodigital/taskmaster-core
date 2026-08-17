# 0003 — Detect external change, never merge automatically

## CONTEXT

ADR 0001 keeps the authoritative task list in memory. If a second application instance, an editor,
or a sync tool writes the store after it was loaded, the in-memory copy is stale and a naive save
would overwrite whatever the other writer did. Something has to decide what happens at that moment,
and the choice is between resolving the divergence automatically and refusing to guess.

## DECISION

Every save compares the file fingerprint held by the caller against the store's current fingerprint,
and on a difference writes nothing and reports the external change to the user.

## RATIONALE

Automatic merging does not prevent data loss here, it hides it: a last-write-wins rule destroys one
of the two edits silently and offers the user no moment to notice. Detection loses nothing — both
versions still exist and the person deciding is present at the keyboard, which is the condition that
makes asking cheap. This is the behaviour git, text editors, and databases with optimistic
concurrency all converge on: report the conflict, do not invent a resolution. Merging would also
require a stable identifier and a modification timestamp on every task record, plus a retained
baseline snapshot and a conflict-resolution rule with its own test matrix — a large amount of
machinery bought for a case that a single-user local tool rarely reaches.

## ALTERNATIVES

- **Automatic merge (last write wins)** — rejected: destroys one edit silently, which is the outcome
  detection exists to prevent.
- **A lock file marking the store as in use** — rejected: an abnormal exit leaves the lock behind and
  the application cannot be reopened without manual cleanup, trading a rare failure for a
  recurring one.
- **Do nothing and accept the overwrite** — rejected: this is the data loss itself, merely undetected.
- **Three-way merge with identifiers and timestamps** — rejected: reintroduces the conflict
  resolution that choosing a local single-user store was meant to avoid.

## CONSEQUENCES

### POSITIVE

- No edit is ever destroyed without the user being told.
- Task records need no identifier and no modification timestamp.
- No conflict-resolution rules to specify, implement, or test.

### NEGATIVE

- The user is occasionally interrupted by a report and must reload, rather than the situation
  resolving itself.
- Load and save must both carry a fingerprint, so the port signature is wider than a plain
  read/write pair — see ADR 0005.

## STATUS

Accepted

## RELATED_REQS

- REQ-ARCH-003
- REQ-ARCH-019
- REQ-ARCH-020
