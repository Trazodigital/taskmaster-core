# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`taskmaster-core` is a fresh product scaffold, not yet an application. `src/` and `tests/` are empty
(`.gitkeep` only). It is built under the **Team_Repo_Quality_Framework_Gentle.ai V-Model quality
framework**, vendored as a git submodule at `.framework/`. `.framework/AGENTS.md` is the authoritative
agent-facing index (skills, scripts, phase rules) — read it before doing any work here; this file only
covers what's specific to running commands in this repo.

## Source of truth

The Quality Framework documentation is the primary and authoritative reference for this project —
above anything in this file. Always read and follow it first:

- `.framework/01_DOCU_QualityFramework/DOCUMENTATION_Quality-framework_Gentle.ai.md`
- `.framework/01_DOCU_QualityFramework/USER_MANUAL.md`
- `.framework/01_DOCU_QualityFramework/OPEN_ACTIONS.md`

If anything here conflicts with those documents, the framework documentation wins.

## Setup

```bash
git submodule update --init --recursive        # if cloned without --recurse-submodules
git config core.hooksPath .framework/templates/hooks   # commit-message + branch-name gates
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
```

## Commands

Toolchain: Python 3.14, pip, flake8, black, pytest, bandit, coverage.py (declared in `tech-stack.yaml`).

```bash
flake8 src/                                    # lint
black --check src/                             # format check
pytest tests/ src/ --cov=src                   # unit tests + coverage
bandit -r src/                                 # security scan
bash scripts/local_dry_CI_run_before_commit.sh # run the full CI gate set locally before pushing
```

The exact suite commands (and the full CI gate list) live in `tech-stack-integrations/build-pipeline.yaml`.

## Branch model

Two tracks, both enforced by CI:

- `arch/<slug>` — architecture-only. No changes to `src/` or `tests/`. Runs a reduced gate set
  (`architecture_suites` in `build-pipeline.yaml`). Current branch: `arch/baseline`.
- `feature/<REQ-UID>-<slug>` or `bugfix/<REQ-UID>-<slug>` — implementation. Runs the full gate set and
  requires an architecture layer to already exist.

## Standing rules

- `tech-stack.yaml` and `tech-stack-integrations/*.yaml` are **human-owned** — read to resolve tool
  paths/commands, never create/modify/rename/delete them.
- Strict TDD: no production code before a failing test exists (RED → GREEN → REFACTOR).
- Module-as-directory: each architecture module maps 1:1 to `src/<slug>/`, tests co-located under
  `src/<slug>/tests/`.
- Every REQ-implementing source file carries an `@sdoc[REQ-UID]` marker; non-obvious decisions carry an
  `@adr[NNNN]` marker linked under `docs/adr/`.
- Commits are Conventional Commits and reference at least one REQ UID or issue ID.
- All quality gates hard-gate on violation — no warn-and-continue.
- A framework defect (a gate that passes without checking, an untrue doc, etc.) is logged in
  `FRAMEWORK_FEEDBACK.md`, never silently worked around locally.

## Communication

Reply in this chat in Spanish, clear and direct, avoiding technical jargon — explain things simply.
Code, comments, commits, and any file written to this repo stay in English.

## Docs layout

`docs/requirements/`, `docs/design/`, `docs/adr/`, `docs/architecture/`, `docs/human_documentation/`,
`docs/glossary.md`.
