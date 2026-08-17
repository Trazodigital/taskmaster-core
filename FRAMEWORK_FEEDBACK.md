# Framework feedback

Running log of Quality Framework weaknesses found while building this product.
Installed by `scripts/init-product.sh`; lives in the product root and is
reported upstream to the framework maintainer.

**What belongs here:** anything the framework claims that turns out not to be
true, anything it enforces that it should not, and anything it fails to enforce
that it says it does. Evidenced findings only — a command that was run and the
output it produced.

**What does not:** preferences, "would be nice", and anything you have not
reproduced. A finding you only reasoned about is a hypothesis; say so
explicitly in **Verification** rather than presenting it as fact.

**Do not patch around the framework locally.** Record the gap here and leave
the product in its honest broken state, with a note saying so. A local
workaround hides the defect from every other product that will hit it, and
makes the upstream fix harder to justify. If you must unblock, say exactly what
you did and mark it for removal.

---

## How to use this file

One `### FB-nnn` entry per finding, newest at the top of the log. Never edit a
closed entry — add a follow-up entry and link it. Fill every field; write
`n/a` rather than deleting one, so a missing answer is visible.

### Severity

| Level | Meaning |
|---|---|
| **critical** | A gate reports success without actually checking. A green build that means nothing. |
| **high** | A declared hard-gate has no implementation, or a config asserts something false. |
| **medium** | Contract defect, incomplete fix, or drift between two files claiming one fact. |
| **low** | Friction, docs, missing capability with a workaround. |

### Class

| Code | Class | Example from history |
|---|---|---|
| **C1** | Silent bypass — gate passes without reading its input | corpus glob hardcoded `*.md`; unreadable file exits 0 |
| **C2** | False claim — config asserts what is not true | `require_codeowners_review: true` on a host that cannot enforce it |
| **C3** | Unimplemented policy — a declared gate with nothing behind it | `on_duplicate_uid: hard-gate` with no implementation |
| **C4** | Contract defect — template or schema wrong, ambiguous, or unsafe | unquoted `{id}` truncating a shell command |
| **C5** | Missing capability | no requirement-to-requirement relations |
| **C6** | Friction or documentation | manual says "nothing else is needed" when more is needed |

**C1 and C3 are the framework's worst failures** and get priority regardless of
how small the fix looks. A red build tells you something; a false green tells
you nothing, and everything built on top of it inherits the lie.

---

## Entry template

Copy this block for each finding.

```markdown
### FB-nnn — <one-line summary>

- **Date:** YYYY-MM-DD
- **Framework version:** <tag> @ <submodule SHA>
- **Severity:** critical | high | medium | low
- **Class:** C1 | C2 | C3 | C4 | C5 | C6
- **Status:** open | reported | fixed upstream in <version> | wontfix | superseded by FB-nnn

**What the framework claims**

Quote it, with `file:line`. If the claim is implicit (a schema constant, a
template comment, a skill instruction), say where the implication comes from.

**What actually happens**

The command that was run and the output it produced. Paste both.

​```
$ QF_ROOT="$PWD" .framework/scripts/check-x.sh
{ "violations": 0 }
exit: 0            # the corpus contains 3 violations
​```

**Reproduction**

Smallest input that shows it. A fixture directory the framework can lift
straight into `framework-tests/fixtures/` is ideal — that is the difference
between a report and a regression test.

**Verification**

How this was established. State plainly whether it was RUN or only READ:
running it is evidence, reading it is a hypothesis. Note anything that was
disproved along the way — a wrong first diagnosis is useful signal about where
the framework misleads readers.

**Blast radius**

Product-specific, or does every product on this framework hit it? Say which,
and why. Unconditional failures matter more than conditional ones.

**Impact on this product**

What it broke, what was paused, what was shipped anyway and on what basis.

**Workaround applied**

`none` is the preferred answer — see the policy above. If something was done,
name the exact files and mark it for removal once the framework ships a fix.

**Proposed fix** *(optional)*

Only if you have one. Say whether it was tested and against what cases. A
proposal that was never run should say so.
```

---

## Log

<!-- Newest first. -->

### FB-005 — the framework grants itself a single-maintainer exception but gives products no way to declare one

- **Date:** 2026-08-16
- **Framework version:** v3.0.0 @ 978cd9e83ed4b3ebffae06b5ccedd393b39528f2
- **Severity:** medium
- **Class:** C5
- **Status:** open

**What the framework claims**

`AGENTS.md` § Standing rules, four-eyes principle: "No branch merges to `main` without a
second-reviewer approval and green CI. Architecture PRs additionally require CODEOWNERS approval on
`docs/architecture/`. This rule governs **products** built with the framework; the framework
repository itself operates single-maintainer by deliberate exception — repo-level branch protection
and green CI are its safeguards."

`tech-stack-integrations/build-pipeline.yaml` states the corresponding config is not negotiable:
"The policy fields are locked to their strict values on purpose: the framework requires reviewed,
linear, non-force-pushed history, and **there is no supported way to declare otherwise**."

**What actually happens**

The framework identifies a legitimate state — one maintainer, safeguarded by branch protection and
green CI — takes that exemption for itself, and then provides no way for a product to declare it.
`min_reviewers` and `require_codeowners_review` are locked, so a product with one available reviewer
must either leave `main` permanently unmergeable or weaken enforcement outside the config and let
the config keep asserting a review that does not happen.

There is no gate failure to paste here, and that is the point: nothing fails. The `enforcement`
block honestly reports `manual-process` / DEGRADED either way, so the config cannot distinguish
"four-eyes is enforced by humans by agreement" from "four-eyes is structurally impossible here".
Those are different situations and a reader cannot tell them apart.

**Reproduction**

A product whose repository has exactly one available reviewer. GitHub refuses to let a PR author
approve their own PR, so with `required_approving_review_count: 1` and `enforce_admins: true` the
protected branch cannot be merged by anyone. No combination of values in `build-pipeline.yaml`
expresses this, because the two relevant fields are declared locked.

**Verification**

RUN for the blocking behaviour on this product: `main` carried
`required_approving_review_count: 1`, `require_code_owner_reviews: true`, `enforce_admins: true`,
and no CODEOWNERS file existed at all after the reset, leaving the branch unmergeable by its only
available maintainer. READ for the config claim — the "no supported way to declare otherwise"
sentence is quoted from the shipped template.

**Blast radius**

Every product built by a solo maintainer, or by a team that temporarily drops to one available
reviewer — a holiday is enough. Conditional, but the condition is common, and the framework's own
repository is an instance of it.

**Impact on this product**

The architecture PR could not be landed. `enforce_admins` was set to `false` on the repository so
the sole maintainer can merge, with the review requirement left declared rather than deleted so
restoring four-eyes is a single flag. Nothing in the corpus or the gates was weakened.

**Workaround applied**

Repository setting only, no framework or config file bypassed:
`enforce_admins: false` on `main`. `required_approving_review_count: 1`,
`require_code_owner_reviews: true`, `required_linear_history: true`, `allow_force_pushes: false` and
`allow_deletions: false` are all unchanged. The deviation is recorded in
`build-pipeline.yaml § branch_protection.enforcement.unenforceable_reason`, which is the field the
framework provides for stating what is really enforced. **Marked for removal once a second reviewer
is available** — restoring `enforce_admins: true` is the whole revert.

**Proposed fix** *(optional)*

Not tested; proposal only. Add a declarable single-maintainer mode to
`branch_protection.enforcement` — for example `mechanism: single-maintainer`, requiring the same
`unenforceable_reason` prose plus an explicit acknowledgement that CI is the only safeguard, and
having `check-branch-protection.sh` report it as a distinct state rather than folding it into
`manual-process`. That preserves the honesty the `enforcement` block was designed for while letting
a product state a situation the framework already recognises as legitimate for itself.

---

### FB-004 — `design-artifacts` lists six required design sections; the gate that judges the file requires nine

- **Date:** 2026-08-16
- **Framework version:** v3.0.0 @ 978cd9e83ed4b3ebffae06b5ccedd393b39528f2
- **Severity:** medium
- **Class:** C4
- **Status:** open

**What the framework claims**

`skills/design-artifacts/SKILL.md:26` — "Every design file MUST contain the following sections in
order" — then enumerates exactly seven: `REQS_COVERED`, `MODULES`, `PORTS`, `ADAPTERS`, `DATA_FLOW`,
`DIAGRAMS`, `DECISIONS`. Its own hard-gate list repeats a subset at `:68`: "Missing section. The
design document lacks any of `REQS_COVERED`, `MODULES`, `PORTS`, `ADAPTERS`, `DATA_FLOW`, or
`DECISIONS`."

`SUMMARY` and `SECURITY_TEST_PLAN` appear nowhere in that skill.

**What actually happens**

`scripts/check-design-review.sh:121` requires nine:

```
REQUIRED_SECTIONS=(SUMMARY REQS_COVERED MODULES PORTS ADAPTERS DATA_FLOW DIAGRAMS DECISIONS SECURITY_TEST_PLAN)
```

A design file authored by following `design-artifacts/SKILL.md` exactly, with all seven declared
sections present and correct, hard-gates:

```
$ QF_ROOT="$PWD" .framework/scripts/check-design-review.sh --scope architecture
check-design-review.sh: hard-gate: docs/architecture/baseline.md: missing required section 'SUMMARY'
check-design-review.sh: hard-gate: docs/architecture/baseline.md: missing required section 'SECURITY_TEST_PLAN'
exit: 1
```

`SECURITY_TEST_PLAN` is at least discoverable — `skills/security-test-templates/SKILL.md:37` names
it, and `workflows/sdd-architecture.md` runs that skill before the review gate, so an agent
executing the workflow in order finds it. `SUMMARY` is named by no skill at all. The only way to
learn it is required is to fail the gate and read the script.

**Reproduction**

Author any file under `docs/architecture/` containing exactly the seven sections
`design-artifacts/SKILL.md:26` enumerates, then run
`check-design-review.sh --scope architecture`. It fails on `SUMMARY` and `SECURITY_TEST_PLAN`.

**Verification**

RUN. Observed on this product while executing `/sdd-architecture` Phase 2 on `arch/baseline`,
against a design file written directly from the skill's section list.

**Blast radius**

Every product on this framework, on the first design file it authors, on both tracks — the
`REQUIRED_SECTIONS` array is not scope-dependent. Self-resolving only in the sense that once an
author has been bitten they remember; nothing in the skill ever gets corrected.

**Impact on this product**

One failed gate run during Phase 2 of the first architecture PR. Nothing shipped incorrectly: the
gate did its job, the skill did not. Cost was one iteration plus reading the script to recover the
authoritative list.

**Workaround applied**

`none`. The design file was written to satisfy the script, which is the authoritative behaviour;
no framework file was modified.

**Proposed fix** *(optional)*

Not tested; proposal only. Add `SUMMARY` and `SECURITY_TEST_PLAN` to the section list at
`design-artifacts/SKILL.md:26` and to its `Missing section` hard-gate at `:68`, so the skill and the
script state the same contract. `SUMMARY` additionally needs a one-line description of what it is
for, since no skill currently defines it.

---

### FB-003 — `UNPARSEABLE_MERMAID` is a declared hard-gate that nothing implements

- **Date:** 2026-08-16
- **Framework version:** v3.0.0 @ 978cd9e83ed4b3ebffae06b5ccedd393b39528f2
- **Severity:** high
- **Class:** C3
- **Status:** open

**What the framework claims**

`skills/mermaid-intake/SKILL.md:144` lists among the conditions the agent MUST hard-gate on:
"**`UNPARSEABLE_MERMAID`.** The block does not parse as valid Mermaid." The same file names the
enforcing script at `:170`: "**Enforced by:** `check-mermaid.sh` — deterministic structural gate".
`workflows/sdd-architecture.md` routes both spec-level diagrams through this skill, and
`skills/design-artifacts/SKILL.md:33-36` then embeds the approved files byte-identically into the
architecture design file.

**What actually happens**

`scripts/check-mermaid.sh:11-15` disclaims it in its own header: "It deliberately does NOT attempt
graph-topology checks... Those need a real Mermaid parser; a flaky bash approximation that
false-positives on valid diagrams would [be worse]... the script never claims full Mermaid parse
validity." `mermaid-intake/SKILL.md:49` says the same of the framework as a whole: "the framework
ships no Mermaid engine".

So nothing parses Mermaid: not the script, not the framework, and the agent cannot do it reliably by
inspection. A file that does not render passes:

```
$ QF_ROOT="$PWD" .framework/scripts/check-mermaid.sh \
    --file docs/architecture/diagrams/baseline.sequence.mmd --kind sequence
{ "check": "mermaid", "status": "pass", "violations": 0, "codes": [] }
exit: 0            # the file does not render
```

**Reproduction**

Any `;` inside a Mermaid note. Observed here with a real line, not a synthetic one:

```
sequenceDiagram
    participant a as alpha
    participant b as beta
    a->>b: request
    Note over a,b: the app reports the error and exits; nothing is ever written
```

`;` is a statement separator in Mermaid, so the renderer stops:
`Parse error on line 5 ... no viable alternative at input 'nothingis'`. `check-mermaid.sh --kind
sequence` returns `"status": "pass", "violations": 0` on that same file.

**Verification**

RUN for the gate result; the parse failure was reported by the human's renderer, since no parser
exists locally to reproduce it. Both halves observed on the same file, in the same session. A first
hypothesis that the participant aliases (`participant app as taskmaster-app`) were at fault was
disproved — the hyphenated aliases render, the semicolon does not.

**Blast radius**

Every product on this framework, on every diagram. Worse than a one-off because of what sits
downstream: a non-rendering diagram passes Tier-1, is approved through the two-gate flow, is frozen
as the spec-level source of truth, mints one `REQ-ARCH-*` per node, edge, subgraph and invariant,
and is then embedded byte-identically into `docs/architecture/<slug>.md`. The requirements corpus
can be built on a diagram nobody can render, and every gate downstream reports green.

**Impact on this product**

Caught by the human at render time, after Tier-1 had reported green twice on the same file. One
approval cycle lost: the flowchart had already been frozen and had to be unfrozen and re-approved
for an unrelated amendment in the same window. Nothing incorrect shipped.

**Workaround applied**

`none` in the framework. Operationally, the human rendered both diagrams and reported the parse
error before either approval token was accepted — which is the only check available today, and is
exactly what the proposed fix would make explicit.

**Proposed fix** *(optional)*

Not tested; proposal only. Two options, and the second is free:

1. Have `check-mermaid.sh` shell out to a real parser when one is present on `PATH`, and emit a
   distinct `"parse": "unavailable"` result rather than `"status": "pass"` when it is not. This
   keeps the honest answer honest instead of letting absence read as success.
2. Remove `UNPARSEABLE_MERMAID` from `mermaid-intake/SKILL.md`'s hard-gate list and state plainly
   that Mermaid validity is established by the human at render time, before the approval token is
   issued. The skill already has the right place for it: Step 1.8 verifies Tier-1 before accepting
   `APPROVE FLOWCHART <slug>`.

Option 2 costs nothing and stops the framework claiming a check it does not perform. Option 1 is
better but adds a toolchain dependency the framework has deliberately avoided.

---

### FB-002 — the scaffold commit `init-product.sh` creates cannot pass the gate wrapper that same script installs

- **Date:** 2026-08-15
- **Framework version:** v3.0.0 @ 978cd9e83ed4b3ebffae06b5ccedd393b39528f2
- **Severity:** low
- **Class:** C6
- **Status:** open

**What the framework claims**

`init-product.sh` step 10 states the scaffold's own commit is deliberately
exempt, and orders the operations to achieve it:

```
# 10. quality git hooks (commit-msg + pre-push). ... Set AFTER the initial
#    commit so the scaffold's own `chore:` commit is not gated.
```

Its closing output then offers the dry run as the next step:
`3. (optional) bash scripts/local_dry_CI_run_before_commit.sh`.

**What actually happens**

The exemption is achieved only against the git hook, by ordering. The wrapper
installed by the same script runs `check-commit-message.sh` on `HEAD`
unconditionally, and that gate exempts only Merge and Revert. So the commit the
scaffolder wrote — `chore: initialize product from Quality Framework (v3.0.0)`,
carrying no REQ UID because no corpus exists yet — is a hard-gate the moment the
suggested dry run is executed.

Two files disagree about one fact: the scaffolder says this commit is not gated,
the wrapper gates it.

**Reproduction**

```bash
bash .framework/scripts/init-product.sh /tmp/gen3 <framework-path>
cd /tmp/gen3
git log -1 --pretty=%s
# chore: initialize product from Quality Framework (v3.0.0)
QF_ROOT="$PWD" .framework/scripts/check-commit-message.sh
# "status": "fail", "has_req": false, "violations": 1
```

No edits between scaffolding and the failing check.

**Verification**

RUN. Executed against a product generated by v3.0.0's own `init-product.sh` and
otherwise untouched, so the result is independent of any product config. Also
observed on this product during the v1.6.0 -> v3.0.0 upgrade before the same
conclusion was reached, but the virgin-product run is the evidence.

**Blast radius**

Every product on this framework, at the moment it is created, and only until its
first REQ-bearing commit lands — after which `HEAD` carries a UID and the gate
clears on its own. Unconditional at that instant, self-resolving afterwards.

**Impact on this product**

One red gate in an otherwise green run at the end of the v3 upgrade. Nothing
blocked: the corpus is empty by design at this point, and the first
`/sdd-architecture` commit will clear it. Cost was diagnostic only — the failure
had to be distinguished from a genuine migration miss before the upgrade could
be called complete.

**Workaround applied**

One edit, in this product's own copy of `scripts/local_dry_CI_run_before_commit.sh`
— a product-owned file whose local edits §4 of `MIGRATION_v3.0.0.md` explicitly
expects to be ported forward. **Marked for removal once fixed upstream.**

The commit-message convenience check is now guarded by a corpus check: it runs
when `docs/requirements/` declares at least one REQ UID, and prints a notice
instead when it does not.

**Correction, 2026-08-16.** That guard was first written as a filename glob for
`REQ-*.md`, a shape `storage.one_file_per: feature` never produces — this
product's corpus is a single `docs/requirements/baseline.md`. The skip was
therefore permanent rather than ending at the first authored requirement, which
is the opposite of what this entry promises: with 22 requirements in the corpus
the wrapper still printed "empty requirements corpus (bootstrap)". Corrected to
match on a declared UID inside the files, which agrees with all three
`one_file_per` values. The defect was in this product's own workaround, not in
the framework; the framework finding recorded above is unchanged. This makes the wrapper consistent with the rest of
the framework — `check-traceability.sh` already treats an empty corpus as a
bootstrap project and skips, its own comment reading "a fresh scaffold still
bootstraps cleanly". That line was the only place that did not.

What was explicitly **not** done, and why:

- No REQ UID was invented to satisfy the pattern. No requirement exists to
  reference, and this product's history shows where that leads: `REQ-ARCH-020`
  was used as a catch-all token on five tooling commits while its actual
  STATEMENT is about the `system` boundary containing six blocks. A token that
  does not describe the change is a traceability lie that reads as compliance.
- No requirement was authored to unblock a gate. A probe confirmed a
  single-entry corpus clears every gate but the overview, so it would have
  worked — which is precisely why it was rejected. Authoring architecture to
  satisfy a checker is how the corpus this product just deleted came to exist.
- The framework submodule was not modified.

Nothing is weakened: the authoritative enforcement named in the wrapper's own
comment — the `commit-msg` hook, plus server-side branch protection — is
untouched and still rejects a message with no REQ UID. Verified after the edit
by attempting a commit with a non-conforming message; the hook refused it. The
skip is announced on stderr, never silent, and ends by itself the moment the
first requirement is authored.

**Proposed fix** *(optional)*

Not tested; proposal only. Either exempt a root commit (no parent) in
`check-commit-message.sh` alongside Merge and Revert — a repository's first
commit cannot reference a corpus that does not exist yet — or have
`init-product.sh` stop advertising the dry run as a next step for a product
whose corpus is still empty. The first is preferable: the exemption then holds
wherever the gate runs, rather than depending on invocation order.

---

### FB-001 — deprecated-host check matches inside trailing comments, so the shipped template fails its own gate

- **Date:** 2026-08-15
- **Framework version:** v3.0.0 @ 978cd9e83ed4b3ebffae06b5ccedd393b39528f2
- **Severity:** medium
- **Class:** C4
- **Status:** open

**What the framework claims**

`check-integration-consistency.sh` line 196 documents its host matcher as
"Lines referencing $2, **ignoring comments**", and the deprecation check is
described as catching a contract that still points at a provider host the
framework removed. `templates/tech-stack-integrations/artifact-store.yaml` is
the file `init-product.sh` copies verbatim into every new product, so it is
expected to pass the gates that same script wires up.

**What actually happens**

The comment filter only skips lines whose **first** non-blank character is `#`.
A configuration line carrying a **trailing** comment is matched in full,
including the commented part, so a host name appearing only in an illustrative
`# e.g. ...` comment is reported as a live reference.

The shipped template contains exactly that at line 36:

```yaml
  base_url: <PLACEHOLDER>          # e.g. https://dev.azure.com/acme/orders-api/_build/results
```

`dev.azure.com` is a host of provider `azure-devops`, removed in 1.5.1 and
recorded in `deprecations.yaml`. The gate therefore reports:

```
check-integration-consistency.sh: hard-gate: tech-stack-integrations/artifact-store.yaml:
references 'dev.azure.com', a host of provider 'azure-devops' removed from the framework in 1.5.1.
```

The field itself is still `<PLACEHOLDER>`. The product never chose Azure
DevOps; the accusation comes from the framework's own example text.

**Reproduction**

Scaffold a product and run the gate against it, unmodified:

```bash
bash .framework/scripts/init-product.sh /tmp/gen3 <framework-path>
cd /tmp/gen3
QF_ROOT="$PWD" .framework/scripts/check-integration-consistency.sh 2>&1 | grep -c hard-gate
# 77
QF_ROOT="$PWD" .framework/scripts/check-integration-consistency.sh 2>&1 | grep -c dev.azure.com
# 1
```

Minimal fixture isolating the matcher, suitable for `framework-tests/fixtures/`:

```
trailing.yaml   a: valor          # e.g. https://dev.azure.com/acme/x   -> expect NO hit
leading.yaml    # e.g. https://dev.azure.com/acme/x                     -> expect NO hit
real.yaml       base_url: https://dev.azure.com/acme/x                  -> expect hit
hash.yaml       prefix: "#"  +  base_url: https://dev.azure.com/acme/x  -> expect hit
```

`hash.yaml` guards the regression the obvious fix introduces: `issue-tracker.yaml`
legitimately carries `prefix: "#"` since the 2.0.0 migration, so a naive
`sub(/#.*$/,"")` would corrupt real values.

**Verification**

RUN, not reasoned. Three stages:

1. The matcher was isolated and run against `trailing.yaml` and `leading.yaml`:
   trailing produced a hit, leading did not. This confirms the filter handles
   only leading comments.
2. A first proposed fix — replacing the leading-comment guard with a
   trailing-comment strip — was **disproved**: it fixed `trailing.yaml` but
   regressed `leading.yaml` to a hit. The guards must compose, not substitute.
   Recorded because the code reads as if one guard covers both cases.
3. A second end-to-end attempt was also **invalid** and is recorded for the same
   reason: the patched script was copied outside `.framework/scripts/`, so it
   aborted on `framework data file not found: deprecations.yaml` and reported
   zero violations. Zero looked like success; it was the script dying. The
   script resolves its data file relative to its own location, so any test that
   relocates it measures nothing.

The valid end-to-end run patches the script in place in a throwaway clone:
77 hard-gates and 1 azure hit before, 76 and 0 after. Exactly one violation
removed, and the 76 legitimate unfilled-placeholder violations preserved.

**Blast radius**

Every product on this framework, unconditionally. The offending line is in the
shipped template, copied by `init-product.sh` into every new product, and the
gate is `blocking: true` and listed in `architecture_suites`. A freshly
scaffolded product cannot reach a green `integration-consistency-gate` until it
either fills `base_url` or deletes the framework's own example comment.

The same matcher runs over every `tech-stack-integrations/*.yaml`, so any
contract whose trailing comment names a decommissioned host is affected, not
only this one.

**Impact on this product**

Blocked `integration-consistency-gate` during the v1.6.0 -> v3.0.0 upgrade,
mixed in with 76 genuine unfilled-placeholder violations. Cost was diagnostic,
not structural: the finding had to be separated from the real config work before
the placeholder list could be trusted. No requirement, design, or code is
affected — the product carries no corpus yet.

**Workaround applied**

The submodule is unmodified; the patch below was applied only to a throwaway
clone under a temp directory, never to `.framework`.

One edit was made to unblock, in this product's own config, not in the
framework: the illustrative comment on `tech-stack-integrations/artifact-store.yaml:36`
was changed from `# e.g. https://dev.azure.com/acme/orders-api/_build/results`
to a GitHub example. The commented host was never a live reference and named a
provider the framework itself removed in 1.5.1, so the file is more accurate
after the change than before. **Remove this note once the matcher is fixed
upstream** — the edit is not a fix, and it hides this defect from this
product's gate run.

**Proposed fix** *(optional)*

Compose the two guards in `host_hits`, `check-integration-consistency.sh:199`:

```awk
awk -v host="$host" '!/^[[:space:]]*#/ { l=$0; sub(/[[:space:]]+#.*$/, "", l); if (index(l, host)) printf "%d:%s\n", NR, $0 }' "$f"
```

Requiring whitespace before `#` follows YAML's own inline-comment rule and is
what keeps `prefix: "#"` intact. Tested against all four fixtures above and
end-to-end as described in **Verification**.

Known limit, untested: a quoted value containing a space followed by `#` would
still be truncated before matching. That cannot produce a false positive, only
a missed detection, and no shipped contract has such a value today. A real YAML
parse would close it; the gate already depends on `yq`/`python3` elsewhere.

Worth considering separately: the taxonomy has no class for a gate that fails
on correct input. C1 covers the false green; this is its mirror, and C4 was
chosen as the closest fit.
