#!/usr/bin/env bash
# next_issue.sh [--label dep-sovereignty] [--repo <owner/repo>]
#
# Picks the next open issue to work, oldest first, skipping anything labeled
# `blocked` or `needs-human`. Only returns issues carrying --label (default
# `dep-sovereignty`) — this skill never touches unlabeled backlog.
#
# Prints "<number>\t<title>\t<labels-comma-separated>" for the picked issue,
# or nothing (exit 0) if there's nothing left to work.
#
# Requires: gh (authenticated), jq.

set -euo pipefail

LABEL="dep-sovereignty"
REPO_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label) LABEL="$2"; shift 2 ;;
    --repo) REPO_ARGS=(--repo "$2"); shift 2 ;;
    *) echo "Unrecognized argument: $1" >&2; exit 2 ;;
  esac
done

gh issue list "${REPO_ARGS[@]}" \
  --label "$LABEL" \
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
