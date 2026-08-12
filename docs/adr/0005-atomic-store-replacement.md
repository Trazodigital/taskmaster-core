# 0005 — atomic store replacement

## CONTEXT

ADR 0001 chose a whole-file JSON store but left the write strategy open. A persist is a read-modify-write over the entire store file, so the naive implementation — open the store for writing and stream the new document over it — destroys every stored Task the moment the write is interrupted, and destroys them again whenever the existing content cannot be parsed. REQ-FUNC-005 and REQ-FUNC-006 turn that failure mode into an explicit contract: an unreadable store is never overwritten, and a failed write leaves the previously stored Tasks intact. REQ-ARCH-022 forbids an automatic retry, so the first attempt is the only attempt and it has to be non-destructive.

## DECISION

`JsonFileTaskRepository` writes the new store document to a temporary file in the store's own directory and promotes it with `os.replace`, and it aborts the whole persist before any write when the existing store content does not parse as JSON.

## RATIONALE

`os.replace` is an atomic rename within a single filesystem, so a reader observes either the old document or the new one and never a truncated one. Writing the temporary file into the store's own directory keeps the rename on that filesystem — a temporary file under the system temp directory could land on a different device and degrade the rename into a non-atomic copy. Parsing before writing turns a corrupt store into a read-time error, which is the only point where the original bytes are still recoverable by hand. Both come from the standard library, so ADR 0001's no-third-party-dependency property is preserved.

## ALTERNATIVES

- Truncate and rewrite the store file in place — rejected: an interrupted write leaves a partial JSON document and loses every stored Task.
- Write a `.bak` copy before rewriting in place — rejected: the recovery step is manual and the window between the two writes is still destructive.
- Append-only log with periodic compaction — rejected: buys crash-durability the single-user CLI of ADR 0001 does not need, and costs a compaction story plus a non-human-readable store.
- File locking around the read-modify-write — rejected: guards against concurrent writers, which ADR 0001 already ruled out of scope, and does nothing about an interrupted write.

## CONSEQUENCES

### POSITIVE

- No reader ever observes a partially written store file.
- A corrupt store fails loudly with the original bytes intact, so manual repair stays possible.
- Standard library only; the security-scan surface of REQ-NFR-SEC-001 is unchanged.

### NEGATIVE

- Each persist writes the whole store twice over (temporary file, then rename), which sharpens the scaling limit ADR 0001 already accepted.
- A crash between the temporary write and the rename leaves an orphan temporary file next to the store.
- Atomicity holds per filesystem: a store path whose directory is not writable cannot be persisted to at all, which surfaces as a storage error rather than a fallback.

## STATUS

Accepted

## RELATED_REQS

- REQ-FUNC-004
- REQ-FUNC-005
- REQ-FUNC-006
- REQ-ARCH-021
- REQ-ARCH-022
- REQ-NFR-PERF-002
