#!/usr/bin/env bash
# next_capability.sh [--repo <owner/repo>]
#
# Picks the next open `migration-item` issue to work, oldest first. Skips
# anything labeled `blocked` or `needs-human`. Issues that would need a
# breaking change or a new dependency ARE returned — the loop's step 3.3 is
# responsible for stopping and asking on those, not this script.
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
  --label migration-item \
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
