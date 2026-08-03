# 0004 — hexagonal composition root

## CONTEXT

The framework mandates hexagonal shape and strict TDD. REQ-ARCH-019 and REQ-ARCH-020 fix a trust boundary with `User` as the only external actor. Every port therefore needs a substitutable implementation, and something must decide which implementation runs.

## DECISION

Introduce an `app` module as the single composition root, the only site permitted to instantiate concrete adapters and wire them to ports.

## RATIONALE

If domain modules construct their own adapters, no test can substitute a double without patching internals, and strict TDD becomes impossible. Confining construction to one module makes every other module a pure function of the ports it is handed.

## ALTERNATIVES

- Let each module construct its own adapters — rejected: makes substitution impossible without monkey-patching, defeating the unit suite.
- A dependency-injection framework — rejected: a third-party dependency to solve what explicit wiring in one file already solves.
- Module-level singletons — rejected: shared mutable state leaks between tests and makes ordering significant.

## CONSEQUENCES

### POSITIVE

- Every port can be exercised with an in-memory or fake double, satisfying testability-discipline.
- Swapping the persistence or reminder runtime touches exactly one file.
- The unit and integration suites of build-pipeline.yaml can be cleanly separated.

### NEGATIVE

- `app` must change whenever a port or adapter is added, making it a natural merge-conflict point.
- Wiring is explicit and therefore verbose compared with an auto-wiring container.

## STATUS

Accepted

## RELATED_REQS

- REQ-ARCH-002
- REQ-ARCH-004
- REQ-ARCH-005
- REQ-ARCH-006
- REQ-ARCH-019
- REQ-ARCH-020
- REQ-NFR-SEC-001
