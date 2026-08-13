#!/usr/bin/env bash
# watch_and_merge.sh <pr-number> [--retries N] [--repo <owner/repo>]
#
# Waits for a PR's CI to finish, and on green: merges with a merge commit
# (never squash/rebase) and syncs the local default branch. On red: exits
# non-zero and prints the failing check names so the caller can decide what
# to do next.
#
# --retries here covers *transient* `gh` CLI/network hiccups around the watch
# call itself (default 1 retry) — it is NOT a "push a fix and try again"
# retry. That kind of retry means new commits, which only the caller (with
# code-editing ability) can produce; this script only re-polls the same PR.
#
# Requires: gh (authenticated), git. Assumes the default branch is checked
# out locally and the repo has branch protection requiring the CI check —
# otherwise "green CI" doesn't actually gate the merge on GitHub's side.
#
# Same mechanics as the sibling loop skills' watch_and_merge.sh, kept as its
# own copy so this skill stays self-contained.

set -euo pipefail

PR=""
RETRIES=1
REPO_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --retries)
      RETRIES="$2"; shift 2 ;;
    --repo)
      REPO_ARGS=(--repo "$2"); shift 2 ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)
      if [[ -z "$PR" ]]; then PR="$1"; shift; else
        echo "Unrecognized argument: $1" >&2; exit 2
      fi ;;
  esac
done

if [[ -z "$PR" ]]; then
  echo "Usage: watch_and_merge.sh <pr-number> [--retries N] [--repo <owner/repo>]" >&2
  exit 2
fi

attempt=0
watch_ok=0
until [[ $attempt -gt $RETRIES ]]; do
  if gh pr checks "$PR" "${REPO_ARGS[@]}" --watch; then
    watch_ok=1
    break
  fi
  attempt=$((attempt + 1))
  echo "gh pr checks watch failed (attempt $attempt/$((RETRIES + 1)))" >&2
done

if [[ $watch_ok -ne 1 ]]; then
  echo "--- CI is red (or the watch itself kept failing) on PR #$PR ---" >&2
  gh pr checks "$PR" "${REPO_ARGS[@]}" || true
  echo "Not merging. This is a real failure to report, not something to retry silently." >&2
  exit 1
fi

echo "CI green on PR #$PR — merging with a merge commit."
gh pr merge "$PR" "${REPO_ARGS[@]}" --merge

default_branch="$(gh repo view "${REPO_ARGS[@]}" --json defaultBranchRef --jq .defaultBranchRef.name)"
git fetch origin "$default_branch"
git checkout "$default_branch"
git pull --ff-only origin "$default_branch"

echo "Merged and synced local '$default_branch'."
