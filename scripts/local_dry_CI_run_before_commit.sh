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
# TWO TRACKS. On an `arch/<slug>` branch this runs the architecture suite set
# (build-pipeline.yaml § architecture_suites): the architecture track authors
# requirements and carries no implementation by design, so the code-shaped gates
# have nothing to run against and holding a correct architecture PR to them
# would make it structurally unmergeable. Every other branch runs the full set.
# The BRANCH decides — there is no flag to opt a feature branch into the
# reduced set, because that is what a bypass would look like.
#
# Usage: bash scripts/local_dry_CI_run_before_commit.sh [--branch NAME]
#        QF_BRANCH=arch/foo bash scripts/local_dry_CI_run_before_commit.sh
set -euo pipefail

PROG=$(basename "$0")
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FW="$ROOT/.framework/scripts"

BRANCH="${QF_BRANCH:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --branch) BRANCH="${2:-}"; shift 2 ;;
    -h|--help) echo "Usage: $PROG [--branch NAME]" >&2; exit 2 ;;
    *) echo "$PROG: unknown argument: $1" >&2; exit 2 ;;
  esac
done

# In CI the checkout is a detached merge commit, so `rev-parse` reports HEAD
# rather than the real branch. CI passes the PR head explicitly via QF_BRANCH;
# the fallback is for local runs, where HEAD is the branch you are on.
if [ -z "$BRANCH" ]; then
  BRANCH=$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
fi

ARCH_TRACK=0
case "$BRANCH" in
  arch/*) ARCH_TRACK=1 ;;
esac

# The branch name is chosen by whoever opened the PR — on a fork it is entirely
# attacker-controlled. So `arch/<slug>` on its own MUST NOT be enough to buy a
# reduced gate set, or naming a branch would be a supported way to switch gates
# off. The architecture track is only safe because an architecture PR carries no
# implementation ("Architecture PRs never contain source code" — USER_MANUAL.md
# § 6.2), and until now nothing enforced that: it was an agent-time rule, not a
# gate. Enforce it here, where the reduced set is actually chosen.
assert_no_implementation() {
  local base="${QF_BASE_SHA:-}" touched
  if [ -z "$base" ]; then
    echo "$PROG: note: no QF_BASE_SHA — cannot diff against the base here." >&2
    echo "$PROG: the no-implementation invariant is enforced in CI, which supplies it." >&2
    return 0
  fi
  if ! git -C "$ROOT" rev-parse --verify --quiet "$base^{commit}" >/dev/null; then
    echo "$PROG: QF_BASE_SHA '$base' is not a commit in this repository" >&2
    exit 1
  fi
  touched=$(git -C "$ROOT" diff --name-only "$base"...HEAD -- src tests 2>/dev/null || true)
  if [ -n "$touched" ]; then
    echo "$PROG: hard-gate: architecture branch '$BRANCH' modifies implementation:" >&2
    # read-loop, not word-splitting: a path may legally contain spaces
    while IFS= read -r p; do [ -n "$p" ] && echo "  $p" >&2; done <<< "$touched"
    echo "$PROG: architecture PRs carry no code — move this to a feature/ branch." >&2
    echo "$PROG: (the reduced architecture gate set is only sound for a PR with no implementation)" >&2
    exit 1
  fi
}

echo "$PROG: dry run of the gates CI will enforce — optional local preview, run before you push." >&2
if [ "$ARCH_TRACK" -eq 1 ]; then
  echo "$PROG: branch '$BRANCH' is on the ARCHITECTURE track — running the architecture suite set." >&2
  echo "$PROG: implementation-shaped gates (marker coverage, module structure) are NOT enforced here." >&2
fi

if [ ! -x "$FW/check-integration-consistency.sh" ] || [ ! -x "$FW/check-traceability.sh" ]; then
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
# Runs first: every gate below resolves its behaviour from the integration
# contracts, so an unfilled or incoherent contract makes their results
# meaningless. Fail on the config before trusting anything built on it.
"$FW/check-docs-layout.sh"
"$FW/check-integration-consistency.sh"
"$FW/check-glossary.sh"
"$FW/check-nfr-fields.sh"
"$FW/check-uid-uniqueness.sh"
"$FW/check-relations.sh"
"$FW/check-framework-feedback.sh"
"$FW/check-mermaid.sh" --all
# Is the generated requirements overview still what the corpus produces? Exits
# 0 for a product that never generated one — it binds only what already claims
# to be derived. Runs on both tracks: the architecture track is where the
# corpus changes most, so it is exactly where the document goes stale.
"$FW/check-traceability.sh" --report --overview --check >/dev/null

if [ "$ARCH_TRACK" -eq 1 ]; then
  # Architecture track. Every gate below still hard-gates in full — including
  # orphan markers, which stay a violation on any branch. What is dropped is
  # marker COVERAGE (there is no implementation to cover the REQs yet) and
  # module structure (there is no module tree yet). Nothing is downgraded to a
  # warning; the reduced set is smaller, not softer.
  #
  # Runs FIRST: it establishes the precondition that makes the reduced set
  # sound. If this PR carries implementation, the reduced set is the wrong set
  # and nothing after it should be trusted.
  assert_no_implementation
  "$FW/check-design-review.sh" --scope architecture
  "$FW/check-traceability.sh" --phase verify --architecture-only
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
# Pass the branch we resolved above rather than letting the gate re-derive it:
# under a detached CI checkout it would see `HEAD` and report exempt, so the
# name of the branch actually being merged would never be checked at all.
if [ -n "$BRANCH" ]; then
  "$FW/check-branch-name.sh" --branch "$BRANCH"
else
  "$FW/check-branch-name.sh"
fi
# PRODUCT-OWNED EDIT — see FRAMEWORK_FEEDBACK.md § FB-002. Remove once fixed
# upstream; §4 of MIGRATION_v3.0.0.md is the porting checklist for this file.
#
# The commit-message convenience check is skipped while the requirements corpus
# is empty. That is the bootstrap state the framework already recognises
# everywhere else: check-traceability.sh treats an empty corpus as a bootstrap
# project and skips (its own comment: "a fresh scaffold still bootstraps
# cleanly"). This line was the one place that did not, so the scaffold commit
# init-product.sh writes — which carries no REQ UID, because no requirement
# exists to reference yet — was reported as a hard-gate by the very wrapper
# that same script installs.
#
# Nothing is weakened. The authoritative enforcement named in the comment above
# is the commit-msg hook, which init-product.sh deliberately installs AFTER the
# scaffold commit for exactly this reason (its step 10), plus server-side
# branch protection. Both still apply, unchanged. The skip is announced, never
# silent, and it ends by itself the moment the first requirement is authored.
#
# "Corpus is non-empty" is decided by whether any requirement file DECLARES a
# UID, not by whether a file is NAMED after one. The original condition globbed
# `REQ-*.md`, a shape `storage.one_file_per: feature` never produces — this
# product's corpus lives in `docs/requirements/baseline.md` — so the skip was
# permanent instead of ending at the first authored requirement, exactly the
# opposite of what the paragraph above promises. Matching on content makes the
# condition agree with the configured storage convention for all three
# `one_file_per` values.
if grep -rqE 'REQ-[A-Z]+(-[A-Z]+)*-[0-9]+' docs/requirements --include='*.md' 2>/dev/null; then
  "$FW/check-commit-message.sh"
else
  echo "$PROG: commit-message check skipped — empty requirements corpus (bootstrap); the commit-msg hook and branch protection still enforce it. See FRAMEWORK_FEEDBACK.md FB-002." >&2
fi
echo "$PROG: all gates passed — safe to push (CI will re-check)."
