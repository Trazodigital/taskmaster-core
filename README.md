# gen3

Framework version: v3.0.0 (pinned by the .framework submodule).

Built under the Team_Repo_Quality_Framework_Gentle.ai V-Model quality framework,
vendored as a git submodule at `.framework/`. See `CHANGELOG(framework).md` for
the framework version and `GENTLE_AI_VERSION` for the Gentle-AI CLI this product
was developed with.

## Setup after cloning

```bash
git clone --recurse-submodules <this-repo>
brew install gentleman-programming/tap/gentle-ai   # see GENTLE_AI_VERSION for the version this product used
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

Enable the quality git hooks (commit-message + branch-name gates):

```bash
git config core.hooksPath .framework/templates/hooks
```

## Dry-run the CI gates locally (optional)

Before you push or open a PR, run the same gates CI enforces — on your machine,
in seconds, instead of waiting for a red CI run:

```bash
bash scripts/local_dry_CI_run_before_commit.sh
```

Optional: CI is the authoritative gate. This is a local preview so a push
doesn't surprise you.

## Update the framework

```bash
git submodule update --remote .framework
cp .framework/01_DOCU_QualityFramework/CHANGELOG.md "CHANGELOG(framework).md"
git add .framework "CHANGELOG(framework).md"
git commit -m "chore: bump quality framework"
```
