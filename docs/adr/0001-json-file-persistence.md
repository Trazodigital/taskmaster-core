# 0001 — json file persistence

## CONTEXT

TaskMaster Core must persist Tasks and Spaces across CLI invocations. The product is a single-user command-line tool with no server, no concurrent writers, and no declared deployment target beyond a local machine. REQ-NFR-PERF-002 budgets a p99 write of 1000 ms, which is generous for any local option.

## DECISION

Persist Tasks and Spaces as JSON documents on the local filesystem via the Python standard library `json` module.

## RATIONALE

A single-user CLI has no concurrency, no network, and no multi-tenancy. A database engine would add an installation step, a schema-migration story, and a running process, none of which buys anything the product needs. The stdlib covers it with no third-party dependency, which keeps the security-scan surface of REQ-NFR-SEC-001 minimal.

## ALTERNATIVES

- SQLite — rejected: adds schema migrations and a query layer for a workload that never exceeds a full-file read.
- PostgreSQL — rejected: requires a running server and credentials for a local single-user tool.
- Plain text / CSV — rejected: cannot represent the nested Task-to-Space relationship without a custom parser.

## CONSEQUENCES

### POSITIVE

- No third-party dependency; nothing new enters the security-scan surface.
- Human-readable on disk, which makes debugging and manual repair trivial.
- Whole-file read satisfies the load-before-write ordering of REQ-ARCH-024 without extra machinery.

### NEGATIVE

- Whole-file rewrite per persist does not scale past roughly ten thousand Tasks.
- No transactional guarantee across a concurrent write; acceptable because the CLI is single-user.
- If the product ever grows a server, this decision must be superseded.

## STATUS

Accepted

## RELATED_REQS

- REQ-ARCH-007
- REQ-ARCH-012
- REQ-ARCH-013
- REQ-ARCH-014
- REQ-ARCH-015
- REQ-NFR-PERF-002
