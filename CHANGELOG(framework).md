# Changelog

All notable changes to this Quality Framework are recorded here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The **top entry** is the current framework version. When a project detaches this template (see `USER_MANUAL.md` § 4), the top version at detach time is the project's **baseline framework version**.

---

## [Unreleased]

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
