# Changelog

All notable changes to this Quality Framework are recorded here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The **top entry** is the current framework version. When a project detaches this template (see `USER_MANUAL.md` § 4), the top version at detach time is the project's **baseline framework version**.

## Provenance convention

Every entry that originates outside the maintainer carries an **Origin** line, so a change can be traced back to what caused it years later:

- `Origin: FB-nnn (<product>)` — a product's `FRAMEWORK_FEEDBACK.md` entry. The reporting channel is `skills/framework-feedback/SKILL.md`.
- `Origin: found verifying FB-nnn` — surfaced while confirming another report, not itself reported. Historically the highest-yield category: the framework's own blind spots cluster around the ones a product happened to notice.
- `Origin: internal` — found by the framework's own suite or maintainer.

Reports predating the `FB-nnn` template (v2.0.0 and earlier) are cited as `Origin: product report, <date>`. Their record lives in the release entry that answered them.

**Defect classes** (shared with `templates/FRAMEWORK_FEEDBACK.md`): **C1** silent bypass · **C2** false claim · **C3** unimplemented policy · **C4** contract defect · **C5** missing capability · **C6** friction/docs. C1 and C3 are the framework's worst failures — a gate that reports success without checking, and a declared gate with nothing behind it.

## Migration convention

Every version carries a **Migration** table directly under its heading: the exact edit, where it goes, and whether it is required. `required` means the build fails until it is done. Nothing else in the entry is a migration instruction — if it is not in that table, no action is needed.

## Scope of this file

**This file records what actually changed between releases, and nothing else.**
Every entry is past tense, describes work that shipped in that version, and is
never edited once released.

Nothing here describes work that has not been done. No open items, no planned
improvements, no deferred decisions — a release entry is a permanent statement
about that release, not a status board, and a reader can trust it without
checking whether it is still current.

---

## [Unreleased]

## [3.0.0] - 2026-08-14

**Major. Every product must rewire its pipeline once.** Two breaking changes land together, deliberately: a mandatory generated document, and the end of the suite-staging period that began in 1.6.0. Batching them is the entire reason for a major — a team pays the migration cost once instead of at every minor.

### Migration — from 2.5.0

**Do the config edits first.** `build-pipeline.yaml` must now declare every framework suite, so an incomplete config fails schema validation before any gate runs and you will not see the other items until it passes.

| Do | Where | Required |
|---|---|---|
| declare **every** framework suite in `suites` — nothing is optional now | `build-pipeline.yaml` | **required** |
| add the top-level `architecture_suites:` list | `build-pipeline.yaml` | **required** |
| add `docs-overview-gate` and `traceability-gate-arch` to `required_checks` | `build-pipeline.yaml` | **required** |
| confirm `conventions.file_layout.human_documentation_dir` is declared | `tech-stack.yaml` | **required** |
| re-copy the gate wrapper, or port its `--check` and two-track lines | `scripts/local_dry_CI_run_before_commit.sh` | **required** |
| `check-traceability.sh --report --overview --write` — generate the document | product root | **required** |
| commit the generated `requirements-overview.md` | `docs/human_documentation/` | **required** |

The fastest path is to diff your `build-pipeline.yaml` against `templates/tech-stack-integrations/build-pipeline.yaml` and copy across whatever you are missing; the suite commands are locked by the schema, so they cannot drift from the template anyway.

**Step-by-step guide: [`MIGRATION_v3.0.0.md`](MIGRATION_v3.0.0.md)** — the table above is the checklist; that document is the walkthrough, with the exact commands, the full suite list, and a troubleshooting section keyed to the error messages you will actually see.

**The eight suites promoted to required:** `docs-layout-gate`, `integration-consistency-gate`, `uid-uniqueness-gate`, `relations-gate`, `framework-feedback-gate`, `branch-protection-gate`, `traceability-gate-arch`, `docs-overview-gate`. Most products already declare several — you only add what is missing.

```yaml
  docs-overview-gate:
    command: .framework/scripts/check-traceability.sh --report --overview --check
    triggers: [push, pr]
    blocking: true
    artifacts: []
```

**One exemption: a corpus with zero requirements.** A freshly scaffolded product has nothing to index and stays green — matching `--phase`, which already treats an empty corpus as bootstrap rather than as a failure. Failing a new repo on its first CI run over an index of nothing would teach exactly the wrong lesson about this gate.

**Regenerate after every corpus change.** Adding a requirement without regenerating turns the build red with the diff and the command to fix it.

### Fixed

- **C2 — the generated overview claimed to be derived from a corpus nothing checked it against.** *Origin: maintainer question on the 2.5.0 delivery, before any product hit it.* 2.5.0 shipped a generator whose output carries the header *"Generated from the corpus … do not edit by hand"* and wired it into nothing: no suite, no wrapper line, no CI step. Add a requirement, never regenerate, and the document describes a corpus that no longer exists while still advertising itself as derived from it. A stale generated file is worse than no file — a reader has no way to tell, which is the definition of a false claim.

  This was introduced closing FB-004, a C5. Shipping a generator and calling the finding closed left the same class of defect the framework exists to catch, one layer over.

### Added

- **`check-traceability.sh --report --overview --check` and the `docs-overview-gate` suite.** Regenerates the overview from the current corpus and diffs it against the committed file, hard-gating on any difference with the diff and the exact command to fix it. The one report invocation that gates; every other `--report` shape still never does.

  **Mandatory, not opt-in.** An absent overview is a hard-gate, not a pass. "We never generated it" and "we generated it and let it rot" leave a reader in exactly the same place — no reliable index of what the corpus contains — and only one of them used to fail. Binding the gate to whoever had already done the work, and nobody else, was the wrong way round.

  It also enforces "do not edit by hand" for the first time: a hand-edited overview fails exactly as a stale one does, because to this gate they are the same thing.

  Listed in `required_checks` and in `architecture_suites`. The architecture track is where the corpus changes most, so it is precisely where the document goes stale.

### Changed

- **Every framework suite is now `required` in the schema — the staging period is over.** *Origin: maintainer decision, closing a gap surfaced reviewing the `docs-overview-gate` delivery.* Since 1.6.0, newly added suites were declared in `properties` but left out of `required`, so a product could upgrade before rewiring its pipeline. The cost was that a product could **omit a gate entirely and stay green**: nothing checked that a gate was *declared*, only that it passed when it ran. A gate you can delete is not a gate.

  The schema promised these would become required in 3.0.0, so they land as one batch — promoting only the new one would have made that promise false while still leaving seven ways to opt out. `architecture_suites` becomes required for the same reason: `check-architecture-exists.sh` blocks feature work until the architecture layer exists, so no product is actually opting out of the architecture track.

  This is the more disruptive of the two breaks and the reason for the major. A missing gate is now a **config** error, not a build error — nothing runs until `build-pipeline.yaml` is complete, where previously the build went red with a message naming the fix. Worse first diagnostic, permanently better guarantee: from here, "the pipeline declares every gate the framework defines" is decidable rather than aspirational.

- **`human_documentation/` is no longer ungated.** *Origin: maintainer decision.* 2.2.0 gave the directory the contract "owned by no skill and scanned by **no gate**", and `tech-stack.yaml`, `AGENTS.md`, and the directory's own `README.md` all said so. One file in it is now required and enforced, so all three said something false the moment `docs-overview-gate` shipped; all three are corrected.

  The distinction they were reaching for still holds and is now stated properly: the directory is **never scanned as corpus** — `check-uid-uniqueness.sh` and the other corpus gates all scope to `storage.requirements_dir`, so a summary table full of REQ UIDs still cannot trip a duplicate check. That was always the real guarantee. "Scanned by no gate" was a convenient shorthand for it, and shorthand that stops being true is just a false claim.

## [2.5.0] - 2026-08-14

### Migration — from 2.4.0

**Required: none.** Pull and stay green — this release only adds a report mode and an optional field.

| Do | Where | Required |
|---|---|---|
| run `check-traceability.sh --report --overview --write` to generate the corpus index | product root | optional |
| add `DERIVED_FROM:` to `REQ-ARCH-*` entries as you touch them | `docs/requirements/` | optional |
| delete any hand-written corpus-index document once the generated one lands | `docs/human_documentation/` | optional |

`DERIVED_FROM` is not backfilled and no gate requires it. An entry without it is reported as *inferred* and marked `?`, which is accurate rather than blocked.

### Added

- **`check-traceability.sh --report --overview` — the corpus index.** *Origin: FB-004 (wp-rest-api product), elaborating the `--report` mode proposed at 2.2.0.* A third report shape alongside summary and detail, grouped by the file each requirement is authored in (so `storage.one_file_per: feature` renders as one table per feature file), with columns `UID | Derived from | Statement`.

  It answers a different question from its siblings and reads a different input. Summary and detail both walk the **markers** and answer "is this covered, and by what?". Overview walks the **corpus** and answers "what is in here?" — which is the question a reviewer asks first, and the one the framework had no answer for. Past a few dozen requirements a flat file-by-file read stops being reviewable; the reporting product hit that at 71.

  `--detail` and `--overview` are mutually exclusive and say so rather than silently ranking one over the other. Markdown by default, `--format json` for tooling, matching the existing split. Statements are the entry's first sentence, extracted verbatim.

- **`DERIVED_FROM: node | edge | subgraph | invariant` on `REQ-ARCH-*` entries.** *Origin: FB-004.* Records **which `mermaid-intake` Step 3 rule produced a requirement**, written by the skill that applies the rule rather than re-derived later by pattern-matching statement text.

  The report reads the field when present and infers it from the statement shapes when absent — but reports the two differently, always. A declared value renders as `edge`; an inferred one as `edge ?`, with a footer counting each. That distinction is the whole point: inference works until someone rewords a statement, and then it is wrong with nothing anywhere to catch it. A generator that cannot tell you which of its values are guesses is a generator that goes stale silently, which is exactly what FB-004 filed against its own hand-built one-off.

  It is a **different axis from the UID's type** and deliberately not called `Type`, as FB-004 proposed: `uid.types` already means `ARCH`/`FUNC`/`NFR`, and `REQ-ARCH-007` being type `ARCH` and `DERIVED_FROM: edge` at the same time is not a contradiction. Two things named "type" in one corpus is how a reader ends up reconciling fields that were never in conflict.

- **`--write`, which resolves its own destination.** Writes the overview to `tech-stack.yaml § conventions.file_layout.human_documentation_dir`, resolved rather than hardcoded — a product that renames that directory renames where this lands, with no edit to the gate. Explicit flag rather than a default, so no invocation writes a file the caller did not ask for, and it fails closed (exit 2) when the key or the file is missing rather than writing somewhere arbitrary.

## [2.4.0] - 2026-08-14

### Migration — from 2.3.0

**Required if you use the architecture track** (`/sdd-architecture`, `arch/*` branches). Without it, an architecture PR still cannot pass CI.

| Do | Where | Required |
|---|---|---|
| add the `traceability-gate-arch` suite (command below) to `suites` | `build-pipeline.yaml` | required |
| add the `architecture_suites:` list naming the suites that run on `arch/*` | `build-pipeline.yaml` | required |
| re-copy the gate wrapper, or port its two-track block by hand | `scripts/local_dry_CI_run_before_commit.sh` | required |
| pass `QF_BRANCH: ${{ github.head_ref \|\| github.ref_name }}` to the wrapper step | `.github/workflows/quality-gates.yml` | required |
| pass `QF_BASE_SHA: ${{ github.event.pull_request.base.sha }}` to the same step | `.github/workflows/quality-gates.yml` | required |

```yaml
  traceability-gate-arch:
    command: .framework/scripts/check-traceability.sh --phase verify --architecture-only
    triggers: [push, pr]
    blocking: true
    artifacts: [traceability-matrix]
```

A product that never runs `/sdd-architecture` may omit `architecture_suites` entirely; an `arch/*` branch then runs the full suite set exactly as before. `check-integration-consistency.sh` hard-gates if any entry names a suite `suites` does not declare, so a typo cannot silently drop a gate.

### Fixed

- **C3 — an architecture-only PR structurally could not pass CI.** *Origin: FB-003 (wp-rest-api product).* `workflows/sdd-architecture.md` instructed the agent to run `verification-suite-execution` in `--architecture-only` mode, scoped by `build-pipeline.yaml § suites.architecture`. Neither existed. `suites.architecture` appeared in four prose files — the workflow, the command, `USER_MANUAL.md`, `DOCUMENTATION_*.md` — and in no script, template, or skill.

  Worse than absent: the schema **rejected** it. `build-pipeline.schema.json` declares `suites` with `additionalProperties: false` and `^product-*` as the only extension pattern, so a product writing the key the documentation told it to write failed schema validation. The framework documented a mode, forbade its configuration, and hard-gated the branch that needed it.

  The effect was unconditional, not a corner case. The architecture track carries no implementation *by design* (`workflows/sdd-architecture.md`: "architecture-only — no feature code, no feature tests"), so `check-traceability.sh --phase verify` reported every REQ in the corpus as uncovered — 71 of them, in the reporting product — on the first CI run any new product ever gets.

  Fixed in the gate rather than in the CI YAML, deliberately. `quality-gates.yml` is a provider template copied into a product once at scaffold time; the gate scripts run live from the submodule. Only a fix in the gate reaches products that already exist, hosts that are not GitHub Actions, and the local dry run — and only a fix in the schema stops the config from asserting something false.

  **`--architecture-only` narrows what is enforced; it never softens it.** Orphan markers still hard-gate. The true uncovered counts are still reported, not zeroed, and the JSON carries `"architecture_only": true` with `"marker_coverage": "not-enforced"` so no consumer can mistake this pass for a full verify. The flag is rejected outside `--phase verify` and rejected in `--report` mode, and the branch selects the mode — there is no supported way to put a `feature/*` branch into it.

- **C3 — `arch/<slug>`, a documented precondition, was rejected by the branch-name gate.** *Origin: found verifying FB-003.* `check-branch-name.sh` accepted only `(feature|bugfix)/<REQ-UID>-<slug>`, and `arch/*` was not in its exempt list either — so the branch form required by `workflows/sdd-architecture.md`, `commands/sdd-architecture.md`, and `skills/mermaid-intake/SKILL.md` failed the framework's own gate.

  The reporting product never saw this one: their wrapper runs under `set -e` and died at the traceability gate eight lines earlier. Fixing only what was reported would have moved the same branch from one red gate to the next.

  An architecture branch carries no REQ UID on purpose — the corpus is authored *on* that branch, so no UID exists when it is created. `arch/<slug>` now passes; `arch/Bad_Slug`, `arch/`, `arch/foo/bar`, and `architecture/foo` still hard-gate.

### Added

- **`architecture_suites` in `build-pipeline.yaml`.** The subset of `suites` that runs on an `arch/<slug>` branch. Entries *select* existing suites by name — they cannot define a suite or a command, so the list can choose which gates apply but never weaken one.

  Declared at the top level rather than as `suites.architecture` as FB-003 proposed. `suites` is a map of suite objects, and `verification-suite-execution/SKILL.md` says "execute every suite in `build-pipeline.yaml § suites`"; a list-valued sibling key inside that map would be handed to the suite executor as though it were a suite. Same mechanism the report asked for, in the one position where it cannot be mistaken for a suite.

- **`architecture_suites ⊆ suites` cross-check** in `check-integration-consistency.sh`. JSON Schema validates each entry's shape but cannot check that the name resolves to a suite the same file declares. Unchecked, `glossary-gates` for `glossary-gate` would drop a real gate from the architecture track while the pipeline still reported green — a C1 introduced by the fix for a C3.

- **The no-implementation invariant is now a gate.** *Origin: found reviewing this release's own change, before it shipped.* Track selection reads the branch name — which is chosen by whoever opened the PR, and on a fork is fully attacker-controlled. Left as first written, naming a branch `arch/anything` would have selected the reduced gate set and dropped marker coverage, module structure, and the logging assertion from any PR that asked for it. A supported way to switch gates off by renaming a branch is precisely the C1 this release exists to close, reintroduced by its own fix.

  `arch/*` alone therefore buys nothing. The wrapper hard-gates an architecture branch whose diff touches `src/` or `tests/`, using `QF_BASE_SHA`, and runs that check *first* — before any gate whose result the reduced set would affect. A PR author may pick the track; they may not pick it and ship code under it.

  This makes "Architecture PRs never contain source code" (`USER_MANUAL.md` § 6.2) enforceable for the first time. It was an agent-time rule that assumed a cooperating agent, so a hand-authored PR was never held to it — the same shape as FB-003 itself, one layer up. An unverifiable `QF_BASE_SHA` fails closed; an absent one (local runs, where there is no base) says so plainly rather than implying a check it did not perform.

- **Two-track selection in the gate wrapper.** `local_dry_CI_run_before_commit.sh` resolves the branch (`--branch`, else `QF_BRANCH`, else `git rev-parse`) and runs the architecture set on `arch/*`. Being in the wrapper rather than in GitHub Actions YAML, it applies identically to the local dry run and to every CI host. `quality-gates.yml` now passes `QF_BRANCH` because a CI checkout is a detached merge commit where `rev-parse` reports `HEAD`.

  The same resolved branch is now passed to `check-branch-name.sh`. It previously re-derived it, saw `HEAD` under CI, and reported `exempt` — so the name of the branch actually being merged was never checked in CI at all.

## [2.3.0] - 2026-08-14

### Migration — from 2.2.0

**Required if you adopted 2.2.0's directory.** It was named `docs/reference/` for one release and is now `docs/human_documentation/`.

| Do | Where |
|---|---|
| `git mv docs/reference docs/human_documentation` (only if it exists) | product root |
| `mkdir -p docs/human_documentation` (if you skipped 2.2.0) | product root |
| add `docs-layout-gate` to `suites`, and the gate line to the local runner | `build-pipeline.yaml`, `local_dry_CI_run_before_commit.sh` |

The new gate names any missing directory and prints the exact `mkdir` to fix it, so running it once tells you what to do.

### Changed

- **`docs/reference/` → `docs/human_documentation/`.** *Origin: maintainer, overriding the name chosen in 2.2.0.* The directory keeps its contract exactly — derived, human-readable, owned by no skill, scanned by no gate — and gains the name the original report asked for. Declared in `AGENTS.md § Docs index` and `tech-stack.yaml § conventions.file_layout` as `human_documentation_dir`.

### Added

- **Layout enforcement.** *Origin: maintainer.* New `check-docs-layout.sh` verifies every directory declared in `conventions.file_layout` exists, and hard-gates with the exact `mkdir -p` when one does not. Until now the layout was a convention only `init-product.sh` applied: directories were created once at scaffold time and never checked again, so a product that removed one — or that was scaffolded before a directory was added to the contract — diverged silently, and the skill that needed it failed later, elsewhere, reporting something unrelated.

  It checks the **whole** declared layout, not `human_documentation` specifically. A gate for one directory would have left the identical gap open for the next entry added to the contract — which is exactly how this one arrived.

- **`qf_yaml_keys` in `lib/corpus.sh`.** Needed to enumerate `file_layout`, and added to the shared library rather than copied into the new gate — `check-integration-consistency.sh` already carries a private version, and a third copy is how the corpus helpers diverged in the first place.

## [2.2.0] - 2026-08-14

### Migration — from 2.1.0

**Required: none.** Pull and stay green.

| Do | Where |
|---|---|
| re-run `check-nfr-fields.sh` over the corpus | see the warning below |
| drop the "no UID text in file titles" authoring habit | `docs/requirements/` |
| `mkdir -p docs/reference` for derived documentation | product root |

**Re-run the NFR gate after upgrading.** Any requirement whose heading named a second UID was **skipped entirely** by 2.1.0 and earlier — `nfr_count: 0, exit 0` over a plainly broken requirement. Violations surfacing now are not new regressions; they were never checked.

### Fixed

- **C1 — a requirement whose heading named two UIDs was skipped in silence.** *Origin: FB-001 (product), whose severity this raises from medium to critical.* `qf_block_uid` used `grep -m1 -o`, which stops after the first matching *line* but prints every match *on* it. A heading like `## REQ-NFR-PERF-001 — supersedes REQ-NFR-PERF-000` returned two lines, and the damage differed by caller — one half of it silent:

  | Gate | Result |
  |---|---|
  | `check-uid-uniqueness.sh` | malformed record, **false duplicate**, loud hard-gate |
  | `check-nfr-fields.sh` | garbage type → no NFR match → **requirement skipped**, `exit 0` |

  Verified: a requirement missing `METRIC` with a malformed `THRESHOLD` reported `nfr_count: 0, violations: 0, exit 0`. The report caught the loud half and rated it C4/medium; testing the same root cause through the other gate exposed the silent half. `qf_block_uid` now returns exactly one UID, so no caller can receive more than one regardless of what produced the line.

- **C4 — a file's own title falsely opened a requirement block.** *Origin: FB-001 (product), reproduced byte-for-byte from the supplied fixture.* `qf_split_blocks` treated a heading as a block boundary if a UID appeared *anywhere* on the line, so `# CLI Triggers — REQ-ARCH-002 .. REQ-ARCH-009` — descriptive prose — produced a spurious block that collided with the real declaration below it and hard-gated a valid corpus as a duplicate. A heading now opens a block only when the UID follows the marker directly. The product hit this across eight files on the first real use of `one_file_per: feature`, and had been avoiding UID text in titles as an unwritten habit; that habit can be dropped.

  **Their proposed fix was correct but not sufficient on its own** — it removes the spurious block, so the loud symptom disappears, while the silent skip above survives untouched. Both changes shipped; the "belt-and-suspenders" half turned out to be load-bearing.

### Added

- **C5 — a gate-safe home for derived documentation.** *(named `docs/reference/` in this release; renamed to `docs/human_documentation/` in 2.3.0.)* *Origin: FB-002 (product).* The documented layout named four `docs/` subdirectories, every one of them owned by a skill or scanned by a gate, leaving nowhere to put human-readable material derived *from* the corpus — the reviewable index a 71-requirement architecture needs to be reviewable at all. `docs/requirements/` was not merely wrong by convention but actively unsafe: a summary table listing dozens of UIDs is exactly the shape FB-001 turned into a false duplicate.

  Declared in `AGENTS.md § Docs index` and `tech-stack.yaml § conventions.file_layout`, scaffolded by `init-product.sh`, owned by no skill and **scanned by no gate** — verified by reading each gate's directory resolution: all of them scope to `storage.requirements_dir`, `docs/design/`, `docs/architecture/` or `docs/glossary.md` specifically. Never a source of truth; everything in it exists elsewhere first.

## [2.1.0] - 2026-08-14

### Migration — from 2.0.0

**Required: none.** Pull and stay green. All three would-be breaking changes are phased to 3.0.0.

Optional now, required in 3.0.0 — do them when convenient:

| Do | Where |
|---|---|
| `cp .framework/templates/FRAMEWORK_FEEDBACK.md .` | product root |
| `check_uniqueness: scripts/check-uid-uniqueness.sh` | `requirements-tracker.yaml § commands` |
| same value for `uniqueness_check` | `requirements-tracker.yaml § uid` |
| copy the 5 gate entries added since 1.6.0 | `build-pipeline.yaml § suites` |
| copy the 2 new gate lines | `scripts/local_dry_CI_run_before_commit.sh` |

**Until `check_uniqueness` is set, `on_duplicate_uid` stays unenforced** — the gate now exists, but nothing points at it.

Your own gates now go in `build-pipeline.yaml § suites` under a `product-` prefix.

**Second product report (2026-08-14), filed after migrating to v2.0.0.** Six findings, all verified against source before any change. Two are v2.0.0's own regressions, and the most severe was not in the report at all — it was found by testing whether the product's diagnosis of *its own* script also applied to the framework's gates. It did.

### Fixed

- **C1 — a gate could report success on a corpus it could not read.** *Origin: found verifying FB report 2 (product diagnosed the pattern in its own script; the framework was never tested for it).* A single unreadable requirement file made `check-nfr-fields.sh`, `check-relations.sh` and `check-traceability.sh` print an awk error to stderr and then report `req_count: 0, violations: 0` and **exit 0**. Verified: `check-relations.sh` passed clean over the `dangling` fixture — which contains a real violation — with its one file at mode `000`.

  Root cause, and the reason the obvious guard does not work: the scan loops read blocks through `< <(qf_blocks_of …)`, and **bash does not propagate a failure from inside a process substitution to the parent shell**. `set -e` never fires. Exit codes are no help either — on BSD `grep` a permission error alongside a partial match returns 1, indistinguishable from "no match". So readability is now asserted up front by `qf_assert_corpus_readable` in the caller's own shell, where `die` actually exits. One function in `lib/corpus.sh`; every gate that reads the corpus inherits it.

  This was **introduced by v2.0.0's own fail-closed work** — `qf_resolve_corpus` verified that files matching the extension *exist*, never that they can be *read*. The exact class v2.0.0 was written to eliminate, reintroduced by the helper written to eliminate it. Regression test sets mode `000` at runtime, since git cannot carry it.

- **C3 — `gate.on_duplicate_uid: hard-gate` had nothing behind it.** *Origin: product report 2.* No script performed the check. `check-traceability.sh` collects UIDs through `sort -u`, which discards duplicates *before* any comparison could run, and `uid.uniqueness_check` shipped as `<PLACEHOLDER>` with no real command to point at. New `check-uid-uniqueness.sh`, and `uniqueness_check` / `commands.check_uniqueness` are now schema-locked to it.

  It counts **declarations, not occurrences** — the non-obvious part, and the product's own reviewers found it the hard way. `relations.refines` writes a parent UID a second time as plain text inside a child (`REFINES: REQ-ARCH-005`), so a raw grep over file contents flags a valid requirements graph as duplicated the moment anyone uses relations. Blocks go through `qf_block_uid`, which takes only the first UID per block. Pinned by a `refines-not-a-duplicate` fixture.

- **C2 — v2.0.0 shipped the `uid.pattern` fix half-applied.** *Origin: product report 2.* `templates/tech-stack.yaml § conventions.req_uid_pattern` still carried the old `REQ-[A-Z]+-[0-9]+` after `requirements-tracker.yaml`'s was corrected. Inert (nothing reads that copy) but false, and it is the same two-files-one-fact drift as the v1.5.1 provider orphaning. The consistency test written in v2.0.0 to prevent exactly this recurrence only ever read *one* of the two files, so it passed. It now asserts both agree.

- **C4 — token-quoting was enforced in one schema out of five.** *Origin: product report 2 (found by the runtime gate, which already covered them).* `shellCommandTemplate` guarded only `issue-tracker.schema.json`, while `artifact-store`, `observability-platform` and `secrets-vault` also carry `commands` blocks — the product hit unquoted tokens in two of them. `check-integration-consistency.sh` caught them at gate time, so the defect was real but contained; the schema now matches the gate's coverage rather than trailing it.

### Added

- **Framework-feedback channel.** *Origin: internal, prompted by two product reports arriving as free-form prose.* `templates/FRAMEWORK_FEEDBACK.md` (installed into every product), `skills/framework-feedback/SKILL.md`, and `check-framework-feedback.sh`, plus an `AGENTS.md` standing rule: **a framework weakness is logged, never silently patched around locally.** A local workaround fixes one product and leaves the defect in place for every other product on the same framework.

  The gate is deliberately narrow. Whether an agent *noticed* a weakness is not decidable by a script, and a gate that pretends otherwise fires on nothing useful and gets switched off. It checks only what is decidable: entries that exist carry the evidence needed to act upstream (`Reproduction` and `Verification` are required), severity and class come from fixed sets so triage works, and a `.framework` bump is accounted for as either findings or an explicit `No findings`. **A fresh product with an empty log passes**; the version check is opt-in via `--range`, which CI passes on PRs exactly as `check-commit-range.sh` already does.

  `Verification` requires stating whether a finding was **run or only read**. In the report that prompted this, three of four bugs were invisible from reading the code and appeared only when it was executed.

- **C5 — products can declare their own gates.** *Origin: product report 2.* `build-pipeline.yaml § suites` was closed in both directions — every framework suite required, nothing else permitted — so a product with its own check had nowhere honest to put it. The only workaround was smuggling it in under an existing name like `lint`, which makes the pipeline describe something it is not running: the same false-claim class as the rest of this cycle. `suites` now accepts any `product-<name>` entry with a free-form command. The prefix is mandatory, because an unnamespaced name could collide with a framework suite added later and silently change meaning. Framework-fixed suites stay locked — a test asserts `traceability-gate`'s command still cannot be repointed at `true`.

## [2.0.0] - 2026-08-13

### Migration — from 1.x

**Required. The build fails until these are done.**

| Do | Where |
|---|---|
| `pattern: "REQ-[A-Z]+(-[A-Z]+)*-[0-9]+"` | `requirements-tracker.yaml § uid` |
| same value for `req_uid_pattern` | `tech-stack.yaml § conventions` |
| single-quote every `{token}`: `gh issue close '{id}' …` | `issue-tracker.yaml § commands` |
| add `prefix:` (e.g. `"#"` for GitHub); `{ref}` = as-written, `{id}` = bare | `issue-tracker.yaml § id` |
| add `format: markdown` and a real `file_extension` | `requirements-tracker.yaml § storage` |
| add `enforcement:` (`host-native` needs `verified_by`; otherwise `unenforceable_reason`) | `build-pipeline.yaml § branch_protection` |

**Then re-run `check-nfr-fields.sh`.** Any `REQ-NFR-*` authored under 1.x was **never checked** — the old pattern could not match it. Expect violations that were invisible before; they are not new regressions.

`one_file_per: feature` now works correctly and is the recommended default — see "Only the first requirement in a file was ever checked" under **Fixed** below.

The release originates in a defect report filed from a product built on this
framework. Every claim in it was verified against source before any code
changed; all five held, and verification surfaced two further defects the
report did not name. **Four of the seven were gates that reported success while
checking nothing** — the failure mode this framework exists to prevent.

### Added

- **Requirement relations — `refines` only.** New `check-relations.sh` plus a `REFINES:` field and a `relations.refines` config block. This was the single functional gap left against a dedicated requirements tool: the corpus could trace requirement→code and requirement→test but never requirement→requirement, so "why does this exist?" and "what breaks if I change it?" had no answer. Three checks always run — **every named parent exists** (a relation pointing at a renamed or deleted requirement makes the whole tree untrustworthy while looking authoritative), **nothing refines itself**, and **the graph is acyclic** (Kahn's algorithm; a self-edge is reported once, as a self-reference, not twice). A fourth, `required_for_types`, forces a parent per requirement type and **ships empty on purpose**: enabling it before a corpus is annotated hard-gates every requirement at once, which is how a good gate gets switched off. `--report` renders the tree (Markdown or JSON, both directions) and never gates. Only `refines` is supported — `depends_on` and `conflicts_with` describe ordering and review concerns, form no tree, and answer neither question. Composes with the traceability detail report: walk down from an architecture requirement to its children, each of which already carries the `file:line` of its implementation and tests.
- **`scripts/lib/corpus.sh`** — the first shared library among the gates, holding corpus discovery and per-requirement block splitting. Extracted rather than copied into the relations gate: the most expensive defect this framework has shipped came from exactly that divergence, where the NFR fixtures drifted onto a UID convention the template forbids and the suite went green against a corpus layout no product could have. `check-nfr-fields.sh` was rewired onto it with no behavioural change.
- **Integration-consistency gate.** New `check-integration-consistency.sh` validates the `tech-stack-integrations/` contracts themselves — the failures that live *between* files, or inside files no skill opens. Three invariants: (1) **no unfilled `<PLACEHOLDER>`** in any field of any contract; every template header promised this hard-gate, but the only enforcement was agent-time and scoped to "fields the calling skill needs" (`skills/tech-stack/SKILL.md`), so a stale value in an unread file was invisible to the agent *and* absent from CI; (2) **no unquoted substitution token** in `commands.*`; (3) **no decommissioned or mismatched provider host**. Wired into `local_dry_CI_run_before_commit.sh` and `build-pipeline.yaml` as a blocking suite. New fixtures + unit tests.
- **`deprecations.yaml`** — machine-readable record of known provider hosts and providers the framework has removed. Dropping the Azure DevOps bundle in 1.5.1 orphaned its two sibling contracts (`issue-tracker.yaml`, `artifact-store.yaml`); a product that migrated only its CI kept both pointing at a dead `dev.azure.com` org for months, and a `REQ-ARCH-*` rationale went on citing that as a live decision. Nothing failed, because nothing was looking. Provider removal is now an event a gate can match, and `framework-tests` requires every removal to carry a version and a migration note.
- **Branch-protection enforcement gate.** New `check-branch-protection.sh` plus a `branch_protection.enforcement` block (`mechanism`: `host-native` | `manual-process` | `none`, `verified_by`, `unenforceable_reason`). A `host-native` claim is executed and hard-gates when live protection is absent; `manual-process` / `none` report DEGRADED and pass. Optional for one minor for backward compatibility, then required. Runs in CI rather than the local dry run — it calls the host API, and that is where the credential lives.

- **Traceability report, detailed shape.** `check-traceability.sh --report --detail` emits the same matrix plus the `file:line` of every source and test marker covering each requirement — Markdown to read, JSON (`"source"` / `"tests"` arrays) for tooling. The summary shape is unchanged and stays the compact CI run-summary view; the product CI now publishes both, the detail as an artifact. The linkage was always enforced but never *visible*: marker locations were discarded at collection time, so the matrix could assert that a requirement was implemented and tested without ever pointing at what implemented or tested it.

### Fixed

- **The NFR gate could not see NFR requirements.** `uid.pattern` was schema-locked to `REQ-[A-Z]+-[0-9]+` while the shipped `uid.types` include hyphenated names (`NFR-PERF`, `NFR-SEC`, `NFR-USE`) and `nfr_fields.required_for_types` is schema-*forced* to that hyphenated form. `[A-Z]+` cannot cross a hyphen, so `REQ-NFR-PERF-001` matched nothing: every gate resolving UIDs from that pattern — traceability, nfr-fields, design-review, branch-name, commit-message — was blind to the entire NFR corpus while reporting green. A template-conformant NFR requirement missing `METRIC` *and* carrying a malformed `THRESHOLD` passed the NFR gate with `req_count: 0`. Two independent breakages, both fixed: the pattern is now `REQ-[A-Z]+(-[A-Z]+)*-[0-9]+`, and `uid_prefix()` strips the `REQ-` document prefix before comparing against type names (which are written without it, so the comparison never matched either). The defect survived because every `nfr/*` fixture used a bare `NFR-[A-Z]+-[0-9]+` pattern the template does not permit — the suite never exercised the combination the framework hands to products. A new layer-2 test now requires `uid.pattern` to express every name in `uid.types` and `nfr_fields.required_for_types`.
- **Requirements gates could be silently switched off by config.** `check-traceability.sh` and `check-nfr-fields.sh` read every setting from `requirements-tracker.yaml` except the corpus glob, which was a hardcoded `*.md`. Declaring any other `storage.file_extension` made both scan zero files and **exit 0** — the traceability gate reported "bootstrap corpus, skipped", the NFR gate reported a clean pass, and CI went green over an entirely unchecked corpus. Both now derive the glob from `storage.file_extension`, refuse to run on a `storage.format` they cannot parse, and refuse to report success when a non-empty requirements directory yields zero matching files. A genuinely empty corpus still passes, so a fresh project bootstraps unchanged.
- **Only the first requirement in a file was ever checked.** `check-nfr-fields.sh` treated the first UID in a file as *the* requirement for that file, so `storage.one_file_per: feature` and `project` — both schema-valid — were silently under-enforced: a malformed requirement anywhere after the first passed unnoticed. Requirement files are now split into per-requirement blocks (opened by a column-0 `UID:` line or a markdown heading carrying a UID) and each block is checked independently. Single-requirement files behave exactly as before. `one_file_per: feature` is now the template default: the framework generates one requirement per diagram node/edge/subgraph, which turns a single architecture diagram into dozens of flat files under `requirement`.
- **`{id}` substitution in `issue-tracker.yaml` was shell-injection-shaped.** The template paired an `id.pattern` that includes its own prefix (`#[0-9]+`) with command examples substituting `{id}` **unquoted** — so `gh issue close {id} --comment '…'` rendered `gh issue close #42 --comment '…'`, the shell read `#42` as the start of a comment, and the command silently degraded to a bare `gh issue close` with every later argument discarded, exiting zero. The contract now defines two distinct tokens — `{ref}` (reference as written, prefix included, prose only) and `{id}` (bare identifier, the only token permitted in `commands.*` and `link_url_template`) — adds `id.prefix`, and both the schema and the new consistency gate reject any unquoted token. The identical latent defect in prefix-carrying trackers (`AB#`) is covered by the same rule.

### Changed

- **Dependency rule: static binaries over interpreted packages.** The framework must add no overhead to a product whose language it knows nothing about. A static binary (`git`, `gh`, `yq`) installs beside a product and joins nothing; an interpreted package enters the product's own dependency graph and has to be reconciled with it forever — worst of all when the product is itself written in that language, with its own pinned versions. This is a rule about *coupling*, not about any particular language. Applied here: the scaffolded `quality-gates.yml` now provisions **`yq`** instead of running `pip install pyyaml`, so a product built on this framework carries no interpreted dependency at all. Both parser backends remain supported and interchangeable in `scripts/check-*.sh` — only the default the framework chooses on a product's behalf has changed. `USER_MANUAL § 1.1` documents the preference and the reasoning.
- **Requirements storage stays markdown — StrictDoc rejected.** StrictDoc was evaluated as the default `requirements-tracker.yaml § tool.name` and turned down under the rule above. It is not a substitutable dependency but the requirements tool itself: there is no non-interpreted alternative, it cannot be swapped for a binary, and it would sit in the authoring loop — on every developer's machine and every requirement edit, not just in CI — carrying its own transitive tree to be pinned per product. Secondary: the git-native gates already cover UID uniqueness, NFR fields, marker traceability, and the Implemented/Verified/Accepted/Released matrix (the same reasoning that rejected SQLite in 1.5.0), and markdown keeps requirements reviewable in ordinary diffs and PR comments. The one capability StrictDoc would add that the framework has no answer for is requirement-to-requirement relations (`refines`, parent/child) — revisit only if that becomes a real need. Note that the framework-fixed `@sdoc[<UID>]` marker syntax is a naming convention only: it implies no StrictDoc dependency and works unchanged over markdown.

## [1.6.0] - 2026-08-02

### Added

- **Claude Code entry points for the two-track model.** The framework now ships `commands/{sdd-architecture,sdd-new,sdd-acceptance}.md` — thin wrappers over the canonical workflows — and `init-product.sh` symlinks them into a product's `.claude/commands/`. Previously only Devin auto-discovered the workflows; Claude Code had no entry point for the architecture/acceptance tracks, and its `/sdd-new` ran Gentle-AI's generic **ungated** chain. The framework's gated `sdd-new` deliberately overrides the generic global one (directory-scoped commands win), so feature work in a product runs this framework's gates. The gentle.ai SDD skills themselves are **not** vendored — they stay CLI-managed (`gentle-ai install --scope=workspace`); the framework ships only its own entry points.
- **Architecture-first gate.** New `check-architecture-exists.sh` hard-gates the feature track unless the architecture layer exists — at least one non-`README.md` document under `docs/architecture/` **and** at least one `REQ-ARCH-*` requirement under `docs/requirements/`. Wired as the `sdd-new` precondition and as a branch-conditional (feature/bugfix PRs only) step in the product `quality-gates.yml` — so a hand-authored feature PR that skips the agent is still caught, without blocking the architecture-bootstrap PR. Covered by new fixtures + unit tests.
- **Mermaid structural gate.** New `check-mermaid.sh` moves the *reliably-scriptable* subset of `mermaid-intake`'s Tier-1 checks — block kind (`WRONG_BLOCK_KIND`), subgraph balance (`UNCLOSED_SUBGRAPH`), and sequence message labels (`UNLABELED_MESSAGE`) — out of LLM prose into a deterministic gate (`--all` validates every committed `docs/architecture/diagrams/*.mmd`; wired into the gate wrapper). Graph-topology checks (duplicate node, orphan, unlabeled edge, participant membership) deliberately stay as agent+human critique: a flaky bash approximation that false-positives on valid diagrams would be worse than no gate, and full parse validity needs a Mermaid engine the framework does not depend on. Part of the skill-token reduction effort (checks→scripts); shrinks the largest skill while strengthening enforcement.
- **Structured-logging gate.** `check-traceability.sh --check-logging` (verify phase) closes the gap where the `structured-logging` skill was enforced only by human review: for every implemented REQ it requires an `@sdoc`-marked test that references the `log_format.event_types` **and** the distinctive field names (`event_type`, `req_uid`, `correlation_id`) resolved from `observability-platform.yaml` — a check that can actually fail, unlike a bare `start/end/error` keyword grep. A REQ that emits no runtime behaviour is exempt via a `@no-runtime-events[<UID>]` source marker. Wired into the verify command in `local_dry_CI_run_before_commit.sh`, `build-pipeline.yaml`, and the CI, so it is enforced, not optional. Covered by new fixtures + unit tests.

### Changed

- **IDE-neutral canonical workflows.** The `sdd-architecture` / `sdd-new` / `sdd-acceptance` workflow definitions moved from `.devin/workflows/` to a canonical, IDE-neutral `workflows/`; the `.devin/workflows/*.md` files are now thin discovery stubs that point at them (Devin already follows in-file references every run, so a pointer needs no new capability). All authoritative-definition references (`AGENTS.md`, `USER_MANUAL`, `DOCUMENTATION`, `docs/*/README.md`, affected skills) were repointed to `workflows/`. This decouples the canonical procedure from any single agent host and makes the "IDE-agnostic" claim real.
- **`USER_MANUAL` §0 reframed as an agent-operator bootstrap.** The manual now addresses the AI agent driving a product: install gentle.ai **workspace-scoped** (`--scope=workspace` — skills go local, package installs + MCP stay global by design), verify the framework's gated command symlinks survived the install, then guide the human through the pipeline one step at a time, honoring every gate. Adds a §7.0 architecture precondition and drops the unsupported Cursor slash-command claim (Devin + Claude Code only).

### Removed

- `01_DOCU_QualityFramework/DEVELOPMENT_CONVENTIONS.md` — a redundant, unreferenced duplicate of the standing rules. The authoritative source is `AGENTS.md § "Standing rules"` (always loaded); the standalone doc was orphaned (nothing in the framework's navigation pointed to it) and at risk of drifting from that single source. Retained in git history (added in 1.5.0).

## [1.5.1] - 2026-07-30

### Changed

- CI: bumped GitHub Actions to the Node 24 majors (`actions/checkout@v5`, `actions/setup-python@v6`) in the framework self-CI and the product `quality-gates.yml` template, clearing the Node 20 deprecation warning.
- Renamed the product gate wrapper `qa.sh` → **`local_dry_CI_run_before_commit.sh`** and documented its purpose (USER_MANUAL § 9.3): it is an **optional local dry-run** of the gates CI enforces, run before a push/PR — deliberately *not* wired into a git hook (forcing it would only duplicate CI while slowing you down). The script now prints its purpose on run. Forward-only: existing products keep their own `scripts/qa.sh`.
- CI: the product `quality-gates.yml` now enforces the branch-name and commit-message conventions **PR-aware**. On `pull_request`, `actions/checkout` leaves a detached merge ref, which made those two gates no-ops (branch resolved to `HEAD`; the HEAD message was the synthetic `Merge …`). The workflow now checks `github.head_ref` for the branch and every commit in `base..head` via the new **`check-commit-range.sh`** (checkout uses `fetch-depth: 0` so the range resolves). Corpus gates were unaffected. This gives the two conventions a server-side backstop, not just the local git hooks.

## [1.5.0] - 2026-07-30

### Added

- CI for the framework's **own** repository: `.github/workflows/framework-ci.yml` (GitHub Actions) runs the `framework-tests` self-suite (pytest) + `shellcheck` on every push/PR, so breakage in the framework itself is caught (it immediately surfaced a Linux-only bug — see Fixed). Distinct from the product CI template under `templates/providers/github-actions/`.
- **Formal-acceptance contract.** New `tech-stack-integrations/test-plans.yaml` (+ schema) declares how the framework reads user-oriented **acceptance** evidence (e.g. Azure Test Plans, `TEST-xxx`) for the Phase-5 **"Accepted"** status. This is separate from automated **"Verified"** (Phase 4): acceptance never gates a merge, blocks release only, and reads `unknown` (fail-soft) when its export is absent.
- **Development-convention gates.** New `check-branch-name.sh` (branch is `(feature|bugfix)/<REQ-UID>-<slug>`, typed UID) and `check-commit-message.sh` (Conventional Commits **and** a REQ token — the bare `REQ-xxx subject` form is rejected). Shipped as git hooks (`templates/hooks/{commit-msg,pre-push}`, installed via `core.hooksPath` by `init-product.sh`), wired into the product gate wrapper, and covered by new unit tests.
- **`01_DOCU_QualityFramework/DEVELOPMENT_CONVENTIONS.md`** — the consolidated non-negotiable rules (immutable typed REQ IDs; branch/commit/PR REQ references; tagged releases; computed Implemented/Verified/Accepted/Released status).
- **Traceability report (Tier-0, git-native).** `check-traceability.sh --report` emits the per-REQ **Implemented / Verified / Accepted / Released** matrix as Markdown (default) or JSON. Implemented/Verified from `@sdoc` markers, Accepted from the acceptance export (fail-soft `unknown`), Released via `git tag --contains`. No database, no extra runtime, always current; published to the product CI run summary. (A heavier SQLite + Python + nightly generator was evaluated and **rejected** — git already holds this data.)

### Changed

- **GitHub-native CI.** GitHub Actions is now the framework's single CI provider. Continuous integration lives on GitHub; formal acceptance testing lives in Azure Test Plans (via `test-plans.yaml`) and never runs CI or gates a merge.
- **Standing rules** (`AGENTS.md`): the Conventional Commits rule now explicitly requires a REQ token; a new branch-naming rule is added; and the four-eyes rule is documented as governing products, with the framework repo as a deliberate single-maintainer exception.

### Removed

- The **Azure DevOps CI provider bundle** (`templates/providers/azure-devops/`) and the `scripts/init-product.sh --ci azure-devops` option. The bundle scaffolded Azure Pipelines + Azure Boards + Azure Artifacts, none of which are needed by the GitHub-native model; Azure Test Plans (acceptance) is a distinct service reached through `test-plans.yaml`, not this bundle. `--ci` now accepts only `github-actions`.

### Fixed

- `check-traceability.sh` returned exit 123 on **Linux** when the REQ corpus was empty (GNU `xargs` runs `grep` once on empty input; BSD/macOS `xargs` does not, so it passed locally). This would fail the traceability gate on a freshly scaffolded product's first CI run. Replaced `find … | xargs grep` with `find … -exec grep {} +`, which never invokes grep on an empty set. Surfaced by the framework's own CI.

## [1.4.0] - 2026-07-28

### Added

- **Azure DevOps support.** `scripts/init-product.sh --ci azure-devops` scaffolds an Azure Pipelines CI (`azure-pipelines.yml`) plus pre-filled Azure Boards (`issue-tracker.yaml`) and Azure Pipeline Artifacts (`artifact-store.yaml`) config, leaving only `<AZURE_DEVOPS_ORG>` / `<AZURE_DEVOPS_PROJECT>` to fill. CI provider templates are organized as bundles under `templates/providers/{github-actions,azure-devops}/`, and a new self-test validates provider config variants against the base schemas. Default provider is unchanged (GitHub Actions).
- **Module-as-directory convention + gate.** Every architecture module (`docs/architecture/*.md § MODULES`) maps 1:1 to `src/<slug>/`, self-contained with co-located tests under `src/<slug>/tests/`. Declared by a new standing rule + the `module-structure` skill; enforced by the new `check-module-structure.sh` gate (wired into `build-pipeline.yaml`, `qa.sh`, and the Azure pipeline). `check-traceability.sh` now classifies test-vs-source **per file** (path/name), so co-located tests count correctly.

### Fixed

- The `build-pipeline.yaml` template **and its schema** pinned the framework gate commands to `scripts/check-*.sh`, which don't exist in a scaffolded product (the gate scripts live in `.framework/scripts/`). Corrected both to `.framework/scripts/check-*.sh` (run with `QF_ROOT` = repo root); the traceability gate now runs `--phase verify`.

### Changed

- CI provider templates moved into `templates/providers/` bundles (`quality-gates.yml` → `providers/github-actions/`).

## [1.3.0] - 2026-07-27

**First production-ready release.** The framework is validated end-to-end — the git-submodule consumption model works against real GitHub, `init-product.sh` scaffolds a self-contained product whose gates pass out of the box, and the 37-test self-suite is green (it also surfaced and fixed three verifier bugs along the way). The repository layout is finalized: all product scaffolding lives under `templates/`, and the root carries only framework tooling and documentation.

### Changed

- Moved the product config templates (`tech-stack.yaml`, `tech-stack-integrations/`, `.env.example`) under `templates/`, alongside `qa.sh` and `quality-gates.yml`, so the framework root no longer looks like it holds project config. `init-product.sh` copies from `templates/`; products still receive the config at their own root. Framework self-tests and docs updated accordingly.
- `init-product.sh` now also scaffolds `runtime-observability/{alerts,dashboards,health-checks}/` in new products, matching AGENTS.md.

### Removed

- Vestigial product-placeholder directories left from the detach model: root `src/`, `tests/`, and `runtime-observability/`. They were unused by the framework itself (products create their own via `init-product.sh`).
- Untracked `.codeiumignore` (editor tooling that was accidentally committed) and added it to `.gitignore`.

## [1.2.1] - 2026-07-27

### Changed

- `GENTLE_AI_VERSION` moved product-side. The framework never invokes Gentle-AI, so it declares no version; `init-product.sh` now captures the developer machine's installed Gentle-AI version into the product, and the framework repo no longer ships a `GENTLE_AI_VERSION`. Corrects the v1.2.0 assumption that the framework "targets" a Gentle-AI version.
- USER_MANUAL states how to name the product (the `init-product.sh` path argument, which also becomes the README title) and that the GitHub repository name is a separate choice at publish time.

### Removed

- The interim `PROPOSAL_framework-tests.md` and `PROPOSAL_submodule-consumption.md` design docs, now that both are implemented — their rationale lives in this changelog and git history.

## [1.2.0] - 2026-07-27

### Added

- **Submodule consumption model.** A product now vendors the framework as a git submodule at `.framework/` instead of detaching the template. New `scripts/init-product.sh` scaffolds a product repo (framework submodule + SDD structure + config templates + gate wrapper + CI + version records); `templates/qa.sh` runs the gates with `QF_ROOT` at the product root; `templates/quality-gates.yml` is the product CI.
- **`GENTLE_AI_VERSION`** — records the Gentle-AI CLI version the framework targets; `qa.sh` warns on drift.

### Changed

- **USER_MANUAL / README rewritten** for the submodule flow: § 3 creates a product repo via the scaffolder, § 4 covers clone-with-submodules, § 5 fills config in the product root, § 9.3 runs gates through the submodule in CI, and a new § 10 covers `git submodule update` framework upgrades. The former "detach the template" flow is removed.

### Fixed

- `check-design-review.sh` — locate sibling verifiers relative to the script (`BASH_SOURCE`) instead of `$QF_ROOT/scripts`, so the delegated traceability check runs when the framework is consumed from a submodule.

## [1.1.1] - 2026-07-27

### Added

- Completed the `framework-tests/` self-test suite: layer-1 verifier tests for `check-glossary.sh`, `check-nfr-fields.sh`, and `check-design-review.sh` (fixture-driven), JSON-Schema conformance for the six `tech-stack-integrations` contracts, and layer-2 consistency / drift meta-tests (AGENTS.md path resolution, skill structure, skills index↔dirs bijection, activation map, internal markdown links, config-script/framework-fixed-key resolution). 37 deterministic tests.

### Fixed

- `check-nfr-fields.sh` — the `MEASUREMENT_METHOD` sub-field check passed the loop variable as `awk -v sub=…`; `sub` is a reserved awk built-in, a syntax error on BSD/macOS awk that made the script falsely flag every NFR requirement. Renamed the awk variable to `want`.
- `check-design-review.sh` — awk `\b` word-boundaries are unsupported on BSD/macOS awk, so on macOS every design and architecture file falsely failed the REQS_COVERED and DIAGRAMS checks and the module/port-in-diagram check never ran. Replaced with a portable `([^A-Za-z0-9_]|$)` at the six awk sites.
- `check-design-review.sh` — `mermaid_blocks_content` merged awk stderr into stdout (`2>&1`), so non-mermaid fenced blocks were never rejected on any platform (the mermaid-only mandate was silently unenforced). Removed the redirect.

## [1.1.0] - 2026-07-27

### Added

- `framework-tests/` — a `pytest` self-test suite for the framework itself, kept separate from the downstream product's `tests/`. Covers `check-*.sh` verifier behavior via their CLI contract (layer 1) and framework consistency / drift meta-tests (layer 2); layer-3 agent evals deferred. The traceability verifier is fully covered via golden fixtures; remaining tests ship as skipped stubs per the rollout plan.

### Changed

- `skills/mermaid-intake/SKILL.md` — normalized the shared ownership hard-gate label to the prose form (`Ownership violation attempt.`) used by the other skills; mermaid-intake's domain-specific gate codes are unchanged. Surfaced by the new drift test.

## [1.0.0] - 2026-07-19

### Initial baseline

- V-Model SDD Quality Framework wrapping Gentle-AI's shipped `sdd-*` skills.
- Two-track development model: `/sdd-architecture` (system) and `/sdd-new` (feature), with `architecture-protection` as hard-gate step 0 of every feature workflow.
- Skills under `skills/` covering Phases 1–6:
  - Phase 1: `requirements-authoring`, `domain-glossary`, `nfr-measurability`, `traceability-gate`, `mermaid-intake`.
  - Phase 2: `design-artifacts`, `testability-discipline`, `security-test-templates`, `design-review-gate`.
  - Phase 3: `tdd-cycle-enforcement`, `adr-discipline`, `structured-logging`, `env-config-awareness`.
  - Phase 4: `verification-suite-execution`, `code-review-gate`.
  - Phase 5–6: `system-acceptance-gate`, `production-observability`.
  - Cross-cutting: `tech-stack`, `architecture-protection`.
- Deterministic verifier scripts under `scripts/`: `check-traceability.sh`, `check-glossary.sh`, `check-nfr-fields.sh`, `check-design-review.sh`.
- Host-native workflows under `.devin/workflows/`: `sdd-architecture.md`, `sdd-new.md`, `sdd-acceptance.md`.
- Integration contracts under `tech-stack-integrations/`: `build-pipeline`, `issue-tracker`, `requirements-tracker`, `artifact-store`, `secrets-vault`, `observability-platform` (YAML + JSON Schema).
- Root files: `AGENTS.md`, `tech-stack.yaml`, `.env.example`, `.gitignore`.
- Documentation under `01_DOCU_QualityFramework/`: `USER_MANUAL.md`, `DOCUMENTATION_Quality-framework_Gentle.ai.md`.

[Unreleased]: https://github.com/Trazodigital/Team_Repo_Quality_Framework_Gentle.ai/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/Trazodigital/Team_Repo_Quality_Framework_Gentle.ai/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/Trazodigital/Team_Repo_Quality_Framework_Gentle.ai/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/Trazodigital/Team_Repo_Quality_Framework_Gentle.ai/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/Trazodigital/Team_Repo_Quality_Framework_Gentle.ai/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/Trazodigital/Team_Repo_Quality_Framework_Gentle.ai/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/Trazodigital/Team_Repo_Quality_Framework_Gentle.ai/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Trazodigital/Team_Repo_Quality_Framework_Gentle.ai/releases/tag/v1.0.0
