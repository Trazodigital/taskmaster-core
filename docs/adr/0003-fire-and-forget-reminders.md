# 0003 — fire and forget reminders

## CONTEXT

REQ-ARCH-026 and REQ-ARCH-027 fix both reminder messages as fire-and-forget, and the frozen sequence diagram carries explicit notes to that effect. A design must decide what the system may claim about delivery it never confirmed.

## DECISION

Treat `task due-date reached` and `deliver reminder` as fire-and-forget, and never record or report a Reminder as confirmed-delivered.

## RATIONALE

Blocking a due-date sweep on delivery acknowledgement would let one unavailable output channel stall evaluation of every remaining Overdue Task. Recording an unconfirmed dispatch as delivered would be a lie the system tells its own audit trail, which is worse than admitting the gap.

## ALTERNATIVES

- Synchronous acknowledged delivery — rejected: one slow channel stalls the whole sweep, breaking the latency budget of REQ-NFR-PERF-001.
- Persisted delivery receipts with retry — rejected: requires durable queue state that no requirement asks for.
- Best-effort dispatch reported as delivered — rejected: records an unverified claim as fact.

## CONSEQUENCES

### POSITIVE

- A due-date sweep always completes, satisfying REQ-ARCH-029 regardless of channel health.
- The system never overstates what it knows about delivery.
- `notifications` can be swapped for any channel without changing the `tasks` contract.

### NEGATIVE

- A Reminder can be silently lost with no record.
- Any future delivery guarantee requires superseding this ADR and adding durable state.

## STATUS

Accepted

## RELATED_REQS

- REQ-ARCH-017
- REQ-ARCH-018
- REQ-ARCH-026
- REQ-ARCH-027
- REQ-ARCH-029
