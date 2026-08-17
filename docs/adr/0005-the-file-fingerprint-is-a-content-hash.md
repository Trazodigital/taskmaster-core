# 0005 — The file fingerprint is a content hash

## CONTEXT

ADR 0003 makes every save compare a fingerprint held by the caller against the store's current
fingerprint. That comparison is the entire mechanism protecting the user from an unnoticed
overwrite, so the reliability of the whole decision reduces to how the fingerprint is derived. Two
candidates were available: filesystem metadata, and a hash of the stored bytes.

## DECISION

The file fingerprint is a hash of the store's bytes, computed at read time and recomputed
immediately before every write.

## RATIONALE

A modification timestamp is cheaper — a stat instead of a read — but it can fail to distinguish two
writes that land within the same clock resolution, and it is affected by clock adjustments and by
tools that preserve timestamps when rewriting a file. Each of those makes the comparison report
"unchanged" for a store that did change, which is exactly the silent overwrite ADR 0003 exists to
prevent. A content hash cannot report a false match. Its cost is reading a file that ADR 0002 keeps
small, on an operation that already happens at human speed, so the cheaper option buys nothing that
matters and gives up the one property that does.

## ALTERNATIVES

- **Modification timestamp** — rejected: can report "unchanged" for a store that changed, which
  turns the protection into a false sense of one.
- **Size plus modification timestamp** — rejected: narrows the failure window without closing it; an
  edit that preserves length still slips through.
- **A monotonic version counter written into the file** — rejected: only works if every writer
  cooperates, and hand-editing the store — a property ADR 0002 deliberately keeps — makes that
  assumption false.

## CONSEQUENCES

### POSITIVE

- The comparison never reports a false match, so external-change detection is as reliable as the
  decision that depends on it.
- No dependency on clock behaviour or on filesystem timestamp resolution.
- Works even when the store is edited by a text editor or replaced by a sync tool.

### NEGATIVE

- Saving reads the store before writing it, so a save touches the file twice.
- The cost grows with store size; bounded in practice by ADR 0002 keeping the store small and by
  `REQ-NFR-PERF-001`.

## STATUS

Accepted

## RELATED_REQS

- REQ-ARCH-003
- REQ-ARCH-012
- REQ-ARCH-019
