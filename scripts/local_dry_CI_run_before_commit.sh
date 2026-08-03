#!/usr/bin/env bash
# local_dry_CI_run_before_commit.sh
#
# A LOCAL DRY RUN of the gates your CI enforces — run it before you push / open
# a PR to catch failures on your machine instead of in a red CI run. It is
# OPTIONAL: CI is the authoritative gate; this is a fast local preview.
#
# The framework is vendored as a git submodule at .framework/. QF_ROOT is set to
# the product root so every gate resolves config, docs, src, and tests here.
# Installed into a product by scripts/init-product.sh; safe to commit and edit.
#
# The gate set is track-aware. On an arch/<slug> branch the architecture track
# runs (metadata-only, per workflows/sdd-architecture.md); every other branch
# runs the full feature track. Override the detected branch with QF_BRANCH.
#
# Usage: bash scripts/local_dry_CI_run_before_commit.sh
#        QF_BRANCH=arch/my-slug bash scripts/local_dry_CI_run_before_commit.sh
set -euo pipefail

PROG=$(basename "$0")
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FW="$ROOT/.framework/scripts"

echo "$PROG: dry run of the gates CI will enforce — optional local preview, run before you push." >&2

if [ ! -x "$FW/check-traceability.sh" ]; then
  echo "$PROG: framework submodule not initialised — run:" >&2
  echo "  git submodule update --init --recursive" >&2
  exit 2
fi

# Warn (do not fail) if the installed Gentle-AI CLI differs from the version this
# product was developed with (recorded in GENTLE_AI_VERSION at scaffold time).
if [ -f "$ROOT/GENTLE_AI_VERSION" ] && command -v gentle-ai >/dev/null 2>&1; then
  want="$(tr -d '[:space:]' < "$ROOT/GENTLE_AI_VERSION")"
  have="$(gentle-ai --version 2>/dev/null | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true)"
  if [ "$want" != "unknown" ] && [ -n "$have" ] && [ "${want#v}" != "${have#v}" ]; then
    echo "$PROG: warning: Gentle-AI ${have} installed; product was developed with ${want} (see GENTLE_AI_VERSION)" >&2
  fi
fi

# Resolve the branch under test, then select the gate track. In a CI
# pull_request checkout HEAD is a detached merge commit, so prefer the refs
# GitHub exports: GITHUB_HEAD_REF on pull_request, GITHUB_REF_NAME on push.
# QF_BRANCH overrides everything for manual runs.
BRANCH="${QF_BRANCH:-${GITHUB_HEAD_REF:-${GITHUB_REF_NAME:-}}}"
if [ -z "$BRANCH" ]; then
  BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)"
fi

case "$BRANCH" in
  arch/*) TRACK=architecture ;;
  *)      TRACK=feature ;;
esac

echo "$PROG: branch '$BRANCH' -> $TRACK track." >&2

export QF_ROOT="$ROOT"

# Gates that hold on both tracks.
"$FW/check-glossary.sh"
"$FW/check-nfr-fields.sh"
"$FW/check-mermaid.sh" --all

if [ "$TRACK" = architecture ]; then
  # Architecture PRs are metadata-only: workflows/sdd-architecture.md forbids
  # any change under src/ or tests/ ("Implementation drift") and skips Phase 3
  # entirely. So the two feature-track gates below cannot hold here by
  # construction, and are deliberately not run:
  #
  #   check-module-structure.sh          — requires src/<slug>/ for every module
  #                                        declared in docs/architecture/*.md,
  #                                        which is exactly the code an
  #                                        architecture PR may not carry.
  #   check-traceability.sh --phase verify — requires a test AND source marker
  #                                        per REQ; the architecture track only
  #                                        ever reaches --phase spec.
  #
  # This implements the scoping that sdd-architecture.md Phase 4 already
  # specifies for verification-suite-execution --architecture-only.
  "$FW/check-design-review.sh" --scope architecture
  "$FW/check-traceability.sh" --phase spec
else
  "$FW/check-design-review.sh"
  "$FW/check-module-structure.sh"
  "$FW/check-traceability.sh" --phase verify --check-logging
fi

# Git-event gates. These are lenient on integration branches (main/master/
# release/*) and on a detached HEAD (CI checkout), where they report `exempt`.
# The authoritative enforcement is the installed git hooks (commit-msg,
# pre-push) plus server-side branch protection; these lines are the local /
# CI convenience check.
if [ "$TRACK" = architecture ]; then
  # check-branch-name.sh enforces (feature|bugfix)/<REQ-UID>-<slug> and exempts
  # only main/master/develop/HEAD/release/*. sdd-architecture.md Preconditions
  # #3 mandates arch/<slug>, which that gate would reject, so validate the
  # architecture naming convention here instead of skipping the check.
  if printf '%s' "$BRANCH" | grep -qE '^arch/[a-z][a-z0-9-]*$'; then
    echo "$PROG: branch '$BRANCH' matches the architecture convention arch/<slug>." >&2
  else
    echo "$PROG: hard-gate: architecture branch '$BRANCH' does not match 'arch/<slug>' (slug: ^[a-z][a-z0-9-]*\$)." >&2
    exit 1
  fi
else
  "$FW/check-branch-name.sh"
fi
"$FW/check-commit-message.sh"
echo "$PROG: all gates passed — safe to push (CI will re-check)."
