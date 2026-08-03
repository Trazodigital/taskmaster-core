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
# Usage: bash scripts/local_dry_CI_run_before_commit.sh
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

export QF_ROOT="$ROOT"
"$FW/check-glossary.sh"
"$FW/check-nfr-fields.sh"
"$FW/check-design-review.sh"
"$FW/check-module-structure.sh"
"$FW/check-mermaid.sh" --all
"$FW/check-traceability.sh" --phase verify --check-logging

# Git-event gates. These are lenient on integration branches (main/master/
# release/*) and on a detached HEAD (CI checkout), where they report `exempt`.
# The authoritative enforcement is the installed git hooks (commit-msg,
# pre-push) plus server-side branch protection; these lines are the local /
# CI convenience check.
"$FW/check-branch-name.sh"
"$FW/check-commit-message.sh"
echo "$PROG: all gates passed — safe to push (CI will re-check)."
