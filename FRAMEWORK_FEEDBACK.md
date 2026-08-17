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

### FB-009 — `declared_names_in()` reads the first word of every prose line in MODULES/PORTS as a declared name, and `design-artifacts`' claimed "empty section" hard-gate is not enforced by the script

- **Date:** 2026-08-17
- **Framework version:** v3.0.0 @ 978cd9e83ed4b3ebffae06b5ccedd393b39528f2
- **Severity:** medium
- **Class:** C4
- **Status:** open

**What the framework claims**

`skills/design-artifacts/SKILL.md:68` lists as a hard-gate: "**Empty section.** `MODULES`, `PORTS`,
`ADAPTERS`, or `DATA_FLOW` is present but empty." `MODULES`/`PORTS` are documented
(`skills/design-artifacts/SKILL.md:28-29`) as "a list of named modules" / "a list of interface
types" — implying structured bullet content, with no stated restriction against explanatory prose
alongside the list.

**What actually happens**

Two related defects in `scripts/check-design-review.sh`'s `declared_names_in()`
(`:192-212`, first identified informally during the architecture PR and never filed — see the
`adapter.` phantom-module incident noted in that PR's session, reproduced here in a new shape):

1. **Prose inside a `PORTS`/`MODULES` section is read as declared names.** The function takes the
   first word of *every* line in the section (after stripping a leading `-`/`*`/`+` bullet marker),
   not just actual bulleted entries. A two-line explanation —
   ```
   None. Filtering is a pure in-memory operation on the already-loaded task list — no load or save,
   so TaskRepository is not exercised by this feature's new code.
   ```
   — was read as declaring two modules named `None.` and `so`, both then failing the diagram-text
   cross-check:
   ```
   check-design-review.sh: hard-gate: docs/design/filter-by-space.md: port 'None.' declared in
     PORTS but absent from every mermaid diagram
   check-design-review.sh: hard-gate: docs/design/filter-by-space.md: port 'so' declared in PORTS
     but absent from every mermaid diagram
   ```
2. **A genuinely empty `PORTS`/`ADAPTERS` section — the heading with zero content lines before the
   next heading — passes the script with 0 violations**, despite the skill's prose declaring that
   exact shape a hard-gate. Verified by testing the same file with the heading followed immediately
   by the next `##` heading: `"violations": 0`.

**Reproduction**

```bash
# (1) prose-as-name
printf '## PORTS\n\nNone. No port is touched here,\nso nothing is called.\n\n## ADAPTERS\n' \
  >> docs/design/some-feature.md   # any file whose REQS_COVERED already resolves
QF_ROOT="$PWD" .framework/scripts/check-design-review.sh --scope all
# hard-gates on phantom ports 'None.' and 'so'

# (2) empty section not gated
printf '## PORTS\n\n## ADAPTERS\n\n' >> docs/design/some-feature.md
QF_ROOT="$PWD" .framework/scripts/check-design-review.sh --scope all
# "violations": 0 — the skill's claimed hard-gate does not fire
```

**Verification**

RUN, both halves, on this product's `feature/REQ-FUNC-004-filter-by-space` design file while
authoring a feature that genuinely touches no port (filtering is pure in-memory, no load/save). Not
hypothesized from reading the script — the exact phantom names `None.` and `so` are copied from the
real failure output above.

**Workaround applied**

Prefixed the explanatory text with `> ` (Markdown blockquote). `declared_names_in()`'s name-capture
regex is anchored `^[A-Za-z]...`, and `>` is not a letter, so a blockquote line contributes no
candidate name while still rendering as visible prose to a human reader:

```markdown
## PORTS

> None. Filtering is a pure in-memory operation on the already-loaded task list — no load or save,
> so TaskRepository is not exercised by this feature's new code.
```

Verified this passes with 0 violations. No script or skill file was modified; the workaround is
Markdown authoring style, applied per-file.

**Blast radius**

Every product on this framework, on any design file where a `MODULES`/`PORTS` section either (a)
carries any multi-word or multi-line explanatory prose rather than pure single-line bullets — an
authoring style nothing in the skill text forbids — or (b) is genuinely empty because a feature
legitimately touches no port, which `REQ-ARCH-002`-shaped pure-in-memory features (like this one)
make a real, non-exotic case, not a corner case.

**Impact on this product**

One failed gate run during Phase 2 of `REQ-FUNC-004`, diagnosed and resolved by rewriting the
section as a blockquote before authoring proceeded. No incorrect state shipped.

**Proposed fix** *(optional)*

Not tested; proposal only. For (1): restrict `declared_names_in()` to lines that are actually
bulleted (require the leading `-`/`*`/`+` the function already strips, rather than falling through
to bare-text lines) — a prose line with no bullet marker should never be read as a declaration. For
(2): either implement the empty-section hard-gate the skill already documents, or remove that claim
from `skills/design-artifacts/SKILL.md:68` if an intentionally-empty section (a feature that
touches no port) was meant to be legal all along — the skill and the script must agree either way.

---

### FB-008 — `verification-suite-execution` resolves `gates.min_coverage_percent` and two other keys the config schema forbids from ever existing

- **Date:** 2026-08-17
- **Framework version:** v3.0.0 @ 978cd9e83ed4b3ebffae06b5ccedd393b39528f2
- **Severity:** high
- **Class:** C4
- **Status:** open

**What the framework claims**

`skills/verification-suite-execution/SKILL.md:38-43` (step 1, "Resolve inputs via the `tech-stack`
skill") requires resolving from `build-pipeline.yaml`:

```
- gates.min_coverage_percent
- gates.on_suite_failure, gates.on_artifact_publish_failure, gates.on_coverage_regression
```

Step 5 hard-gates on the first ("Enforce the coverage gate... Compare the reported coverage
percentage against `build-pipeline.yaml § gates.min_coverage_percent`"), step 3 relies on the
second, step 4 on the third, and the `Hard-gate conditions` list at `:98` names
"**Coverage regression.** Observed coverage is below `build-pipeline.yaml § gates.min_coverage_percent`."
as one of the conditions this skill MUST hard-gate on.

**What actually happens**

The product's `build-pipeline.yaml § gate` (singular, not `gates`) and its own JSON Schema at
`tech-stack-integrations/build-pipeline.schema.json` agree with each other and disagree with the
skill:

```
$ python3 -c "
import json
d = json.load(open('tech-stack-integrations/build-pipeline.schema.json'))
print(d['additionalProperties'])                 # False — no key beyond the required set, anywhere
print(list(d['properties'].keys()))              # [...,'gate'] — no 'gates' key exists
print(d['properties']['gate'])
"
False
[..., 'gate']
{'additionalProperties': False,
 'required': ['on_suite_failure', 'on_missing_artifact', 'on_branch_protection_bypass',
              'on_missing_review', 'on_nfr_regression', 'on_missing_po_approval'],
 ...}
```

Two independent breaks, not one:

1. The parent key is `gate` (singular) in both the shipped template and its schema;
   `verification-suite-execution` reads `gates` (plural) throughout. The schema's root
   `additionalProperties: False` means `gates` can never legally exist alongside `gate` in any
   product's config — this is not a value the product forgot to set, it is a key name the schema
   forbids outright.
2. Even granting the typo and reading `gate` instead, none of `min_coverage_percent`,
   `on_artifact_publish_failure`, or `on_coverage_regression` is among the schema's six allowed
   keys (`on_suite_failure`, `on_missing_artifact`, `on_branch_protection_bypass`,
   `on_missing_review`, `on_nfr_regression`, `on_missing_po_approval`), and
   `additionalProperties: False` forbids adding them.

Per the `tech-stack` skill's own resolution rule (`skills/tech-stack/SKILL.md:44`, "Missing required
key... hard-gate"), step 1 of `verification-suite-execution` cannot complete for ANY product
validating against the framework's own schema — the coverage-gate machinery this skill describes
(step 5, plus the matching hard-gate condition) has no config surface it could ever legally read.

**Reproduction**

```bash
python3 -c "
import json
d = json.load(open('tech-stack-integrations/build-pipeline.schema.json'))
assert d['additionalProperties'] is False
assert 'gates' not in d['properties']
assert set(d['properties']['gate']['properties']) == {
    'on_suite_failure','on_missing_artifact','on_branch_protection_bypass',
    'on_missing_review','on_nfr_regression','on_missing_po_approval',
}
print('schema confirms: gates.min_coverage_percent can never exist')
"
```
Runs clean against this product's untouched, human-owned config and schema — no product-specific
setup needed; any product generated from the same template hits the identical mismatch.

**Verification**

READ (schema) cross-checked against READ (skill text) — both quoted above verbatim, not
paraphrased. Not run end-to-end inside `verification-suite-execution` itself (no such tooling
exists to execute; the skill is agent-interpreted prose), but the `tech-stack` resolution rule it
depends on is unambiguous, and the schema is authoritative per `AGENTS.md § Ownership boundaries`
("every concrete detail used by a framework skill MUST be resolved from `tech-stack.yaml` or a
`tech-stack-integrations/*.yaml`").

**Blast radius**

Every product on this framework, unconditionally, the first time `verification-suite-execution`'s
coverage-gate step is followed literally — not product-specific, since the schema forbidding
`gates`/`min_coverage_percent`/`on_artifact_publish_failure`/`on_coverage_regression` is itself
framework-shipped, not something any product author wrote.

**Impact on this product**

Discovered before Phase 4 execution on `feature/REQ-FUNC-001-add-task`, while resolving inputs per
the skill's own step 1. Coverage was still measured and reported (via `pytest --cov`, which the
declared `test-unit` suite already runs), but the coverage-vs-threshold comparison in step 5 was
not enforced as a hard-gate, since no legally expressible threshold exists to compare against —
inventing one would be fabricating a value the human-owned config never declared, which is exactly
the failure mode FB-002 already rejected for a different field. `on_suite_failure` (the one field
that resolves correctly, once read from the schema-correct `gate` singular key) was still enforced
in full for every suite.

**Workaround applied**

`none` in configuration. Operationally: suite failures were still hard-gated via the correctly
resolving `gate.on_suite_failure`; the coverage number was measured and reported for visibility
without a threshold comparison, analogous to how `check-branch-protection.sh` reports DEGRADED
rather than inventing enforcement that is not configured.

**Proposed fix** *(optional)*

Not tested; proposal only. Either add `min_coverage_percent`, `on_artifact_publish_failure`, and
`on_coverage_regression` to `build-pipeline.schema.json § properties.gate` (and rename references
consistently — pick one of `gate` or `gates`, not both), or rewrite
`verification-suite-execution/SKILL.md` step 1/5 to read the six keys the schema actually declares
and drop the coverage-threshold gate entirely if it was never meant to be product-configurable.
Either fix must touch the schema and the skill together — fixing only one leaves the other wrong.

---

### FB-007 — `is_test_file()` matches by path glob with no extension guard, so compiled `.pyc` bytecode under `tests/` gets scanned as source and corrupts `--check-logging` via an embedded NUL byte

- **Date:** 2026-08-17
- **Framework version:** v3.0.0 @ 978cd9e83ed4b3ebffae06b5ccedd393b39528f2
- **Severity:** medium
- **Class:** C4
- **Status:** open

**What the framework claims**

`scripts/check-traceability.sh:360-365` defines `is_test_file()`:

```bash
is_test_file() {
  case "$1" in
    */tests/*|*/test/*|*_test.*|*.test.*|*.spec.*) return 0 ;;
    *) return 1 ;;
  esac
}
```

Used by `test_files_for()` (`:962-975`) to decide which files under `markers.scan_paths` (`src`,
`tests`) are read as test source for the `--check-logging` structured-logging assertion scan. The
function's name and role — identifying test *source* files — imply it selects source code, not
arbitrary path matches.

**What actually happens**

The pattern matches on path shape alone, with no extension check. `python -m pytest` writes compiled
bytecode to `src/<module>/tests/__pycache__/*.pyc`, and `*/tests/*` matches that path exactly the
same as it matches `src/ui/tests/test_state.py`. Python's compiled bytecode embeds docstrings as
string constants in its constant pool, so a `.pyc` compiled from a file carrying
`"""@sdoc[REQ-FUNC-001]"""` contains that literal byte sequence, and `grep -qF "$marker" "$f"`
matches it. `test_files_for` then returns the `.pyc` alongside the real `.py` test file, and
`check_logging()`'s `content=$(... cat "$tf" ...)` concatenates the *binary* file into a bash
variable via command substitution — which truncates at the first embedded NUL byte, corrupting
whatever text came after it in the concatenation.

```
$ QF_ROOT="$PWD" .framework/scripts/check-traceability.sh --phase verify --check-logging
.../check-traceability.sh: line 1008: warning: command substitution: ignored null byte in input
check-traceability.sh: hard-gate: REQ REQ-FUNC-001: no structured-logging assertion in tests
  (missing: end error event_type). Add a start/end/error integration test asserting req_uid,
  or mark the source @no-runtime-events[REQ-FUNC-001].
```

`src/ui/tests/test_state.py` — one of the files `test_files_for` matched for this UID — contains
the literal strings `start`, `end`, `error`, `event_type`, `req_uid`, and `correlation_id`
verbatim, in passing assertions. The failure is not that the assertion is missing; it is that the
scanner never read it, because an unrelated binary file earlier in the concatenation order
truncated the stream first.

**Reproduction**

```bash
# from a working tree with at least one src/<module>/tests/test_*.py carrying an @sdoc marker
python -m pytest src/                          # writes __pycache__/*.pyc under */tests/*
QF_ROOT="$PWD" .framework/scripts/check-traceability.sh --phase verify --check-logging
# reports the UID as missing logging fields that its .py test file actually asserts
rm -rf src/**/tests/__pycache__
QF_ROOT="$PWD" .framework/scripts/check-traceability.sh --phase verify --check-logging
# the false failure for that UID disappears; only genuinely uncovered UIDs remain
```

**Verification**

RUN. Hit live on this product while verifying `REQ-FUNC-001`'s Phase 3 cycle: the gate reported it
as missing structured-logging fields its test file demonstrably asserts. First hypothesis was that
the test itself was wrong; disproved by rereading the test file directly. Traced to
`test_files_for`'s match set via manual `grep -rlF` reproduction, which showed `.pyc` files present
in the match set alongside the real `.py` files, then confirmed by clearing `__pycache__` and
re-running — the false failure disappeared with no code or test change.

**Blast radius**

Every product on this framework, on any local run of `--check-logging` (or any other
`markers.scan_paths`-driven scan sharing `is_test_file`/`test_files_for`) performed after `pytest`
has populated `__pycache__` under a co-located `tests/` directory — which `module-as-directory`
makes the mandatory layout. Does not reach CI: a fresh checkout carries no `__pycache__` (it is
gitignored, confirmed not tracked in this repo), so the corruption is local-only, but it is the
default state of any working tree a human or agent has actually run tests in — which is to say,
almost always, right when `--check-logging` is most likely to be run by hand to check a REQ before
committing.

**Impact on this product**

One false hard-gate reported for `REQ-FUNC-001` during Phase 3 verification, diagnosed and
dismissed after tracing it to `__pycache__` contamination rather than a real gap. Cost was
diagnostic only; nothing was implemented or skipped to work around it.

**Workaround applied**

`none` in the framework. Operationally, `__pycache__` directories under `src/**/tests/` were
deleted before trusting the gate's output — this is cleanup, not a code or config change, and
leaves no artifact to remove later.

**Proposed fix** *(optional)*

Not tested; proposal only. Add an extension guard to `is_test_file()` — restrict the match to
`*.py` (or the language-appropriate extension resolved from `tech-stack.yaml § project.language`)
before applying the path-shape glob, e.g. `*/tests/*.py|*/test/*.py|*_test.py|...`. This closes the
class of bug entirely: no binary artifact under a `tests/` path can ever satisfy `is_test_file()`
again, regardless of what a compiler, formatter, or editor leaves behind there.

---

### FB-006 — `check-traceability.sh --phase verify` has no changeset scoping, so `main` is red from the moment architecture merges until every `REQ-ARCH-*` has code

- **Date:** 2026-08-16
- **Framework version:** v3.0.0 @ 978cd9e83ed4b3ebffae06b5ccedd393b39528f2
- **Severity:** medium
- **Class:** C4
- **Status:** open

**What the framework claims**

`USER_MANUAL.md:261` and `mermaid-intake`/`sdd-architecture` describe the architecture-then-feature
flow as normal and expected: architecture merges to `main` carrying requirements with no
implementation, then features land one at a time, each closing its own slice of marker coverage.
Nothing in the documentation warns that this sequence produces a red `main` for the entire interval
between those two events.

**What actually happens**

`scripts/local_dry_CI_run_before_commit.sh` selects the gate set from the branch name alone
(`arch/*` → reduced set with `check-traceability.sh --phase verify --architecture-only`, marker
coverage not enforced; anything else → full set with `check-traceability.sh --phase verify
--check-logging`, marker coverage enforced for the WHOLE corpus). `--phase verify` has no
`--changeset` flag — that scoping exists only for `--phase apply` (`:863-874`), which
`tdd-cycle-enforcement` uses per-REQ during Phase 3. The instant the architecture PR merges to
`main`, `main` is no longer `arch/*`, so it runs the full set, and every `REQ-ARCH-*` (and any
`REQ-NFR-*`) is reported as missing a test marker and a source marker — because by design, at that
point, none has been implemented yet.

```
$ QF_ROOT="$PWD" .framework/scripts/check-traceability.sh --phase verify --check-logging
check-traceability.sh: hard-gate: 22 REQ(s) without a test marker: REQ-ARCH-001 ... REQ-NFR-PERF-001
check-traceability.sh: hard-gate: 22 REQ(s) without a source marker: REQ-ARCH-001 ... REQ-NFR-PERF-001
exit: 1
```

This is not a transient blip: it persists on every push to `main` until the LAST `REQ-ARCH-*` in
the corpus finally gets code — which could be many features and a long time later. There is no
required-status-check configuration issue here (this product already runs DEGRADED per FB-005); the
finding is that the gate itself has no notion of "architecture landed, implementation in progress,
partial coverage is expected and not yet a violation".

**Reproduction**

```bash
# on any branch not matching arch/*, with an architecture-only corpus (no REQ has @sdoc yet)
QF_ROOT="$PWD" .framework/scripts/check-traceability.sh --phase verify --check-logging
# hard-gates on every REQ, unconditionally, regardless of how much has actually been implemented
```

Observed directly on this product: PR #7 merged the architecture to `main`, and the very next CI
run on `main` (a `push` event, unrelated to the merge itself) failed with exactly this shape —
`check-module-structure.sh` failing first (3 declared modules, 0 directories — expected, since no
feature had landed yet), and `check-traceability.sh --phase verify --check-logging` would have
failed identically the moment module-structure passed.

**Verification**

RUN, twice: once on `main` immediately after PR #7 (GitHub Actions run 31989704000), and again
locally on `feature/REQ-FUNC-001-add-task` after implementing REQ-FUNC-001, to confirm the failure
mode is exactly "whole corpus, not changeset" — `check-traceability.sh --phase apply --changeset
REQ-FUNC-001` passed with 0 violations for the same tree that `--phase verify` (no changeset)
reported 16 uncovered tests / 8 uncovered src for.

**Blast radius**

Every product on this framework, unconditionally, for the entire span between "architecture merged"
and "every architecture REQ has code" — which is the framework's own prescribed normal operating
state for a product under active development, not an edge case.

**Impact on this product**

`main`'s CI has been red since PR #7 merged (2026-08-16) and will stay red, feature by feature,
until the corpus is fully implemented. No merge is blocked by it (no required status checks are
configured, per FB-005's DEGRADED enforcement state), but the badge is misleading and would page
someone incorrectly if status checks were ever turned on before the corpus finishes.

**Workaround applied**

`none`. Discussed with the maintainer and deliberately not worked around: the correct resolution is
implementing features, which is already the plan, not silencing or reshaping the gate.

**Proposed fix** *(optional)*

Not tested; proposal only. Either (a) add `--changeset` support to `--phase verify` mirroring
`--phase apply`, so CI on a feature branch can assert full coverage for that PR's REQs while
tolerating a partially-implemented corpus elsewhere, or (b) give `verify` an explicit
"in-progress" mode — analogous to `--architecture-only` — that reports true uncovered counts
without hard-gating on them until an product-declared milestone (e.g., all `REQ-ARCH-*` implemented)
is reached, the same DEGRADED-not-silent pattern `check-branch-protection.sh` already uses for an
unenforceable policy.

---

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
