#!/usr/bin/env bash
# next_issue.sh [--repo <owner/repo>]
#
# Picks the next open issue to work, oldest first, from ANY label — unlike
# the sibling skills' next_issue.sh, this one isn't scoped to a skill-owned
# label like `parity-gap`. Skips anything labeled `blocked` or
# `needs-human`. Issues labeled `breaking-change` or `question`/`discussion`
# ARE returned — the loop's triage step is responsible for stopping/skipping
# on those, not this script.
#
# Prints "<number>\t<title>\t<labels-comma-separated>" for the picked issue,
# or nothing (exit 0) if there's nothing left to work.
#
# Requires: gh (authenticated), jq.

set -euo pipefail

REPO_ARGS=()
if [[ "${1:-}" == "--repo" ]]; then
  REPO_ARGS=(--repo "$2")
fi

gh issue list "${REPO_ARGS[@]}" \
  --state open \
  --json number,title,labels,createdAt \
  --limit 200 \
| jq -r '
    map(select(
      (.labels | map(.name) | index("blocked") | not)
      and
      (.labels | map(.name) | index("needs-human") | not)
    ))
    | sort_by(.createdAt)
    | .[0]
    | select(. != null)
    | [.number, .title, (.labels | map(.name) | join(","))]
    | @tsv
  '
