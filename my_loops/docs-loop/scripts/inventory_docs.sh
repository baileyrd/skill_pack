#!/usr/bin/env bash
# inventory_docs.sh [target-dir] [--limit N] [--include-untracked]
#
# Lists every tracked markdown doc in a repo with a drift signal: the date it
# last changed, and how many commits have landed on NON-doc files since that
# change. Sorted by that count, descending — the docs at the top have had the
# most code move underneath them since anyone last touched them.
#
# This ranks candidates for attention. It is NOT a verdict: commit recency is
# not semantics. A doc untouched for a year can be perfectly accurate, and a
# doc edited yesterday can be wrong. docs-loop step 3 does the actual audit
# against ground truth; this only decides where to look first.
#
# Requires: git. Run against a git working tree (the drift signal comes from
# history, so there's nothing useful to report outside one).

set -euo pipefail

TARGET="."
LIMIT=0
INCLUDE_UNTRACKED=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)
      LIMIT="$2"; shift 2 ;;
    --include-untracked)
      INCLUDE_UNTRACKED=1; shift ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)
      TARGET="$1"; shift ;;
  esac
done

if [[ ! -d "$TARGET" ]]; then
  echo "Not a directory: $TARGET" >&2
  exit 2
fi

if ! git -C "$TARGET" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git working tree: $TARGET" >&2
  echo "The drift signal is derived from history — there's nothing to report here." >&2
  exit 2
fi

# Docs whose own churn should NOT count as "code moved": excluded from the
# since-count so a docs-only commit doesn't inflate every other doc's score.
NON_DOC_PATHSPEC=(. ':(exclude)*.md' ':(exclude)*.mdx')

mapfile -t docs < <(git -C "$TARGET" ls-files -- '*.md' '*.mdx' | sort)

if [[ ${#docs[@]} -eq 0 ]]; then
  echo "No tracked *.md/*.mdx files under $TARGET."
  exit 0
fi

rows=""
for doc in "${docs[@]}"; do
  sha="$(git -C "$TARGET" log -1 --format=%H -- "$doc")"
  if [[ -z "$sha" ]]; then
    # Tracked but with no commit touching it (staged-only add).
    rows+="0\tuncommitted\t$doc\n"
    continue
  fi
  last="$(git -C "$TARGET" log -1 --format=%cs -- "$doc")"
  since="$(git -C "$TARGET" rev-list --count "$sha..HEAD" -- "${NON_DOC_PATHSPEC[@]}")"
  rows+="$since\t$last\t$doc\n"
done

echo "docs-loop inventory: $TARGET"
echo
printf '%-14s  %-12s  %s\n' "CODE-COMMITS" "LAST-CHANGED" "DOC"
printf '%-14s  %-12s  %s\n' "SINCE" "" ""

sorted="$(printf '%b' "$rows" | sort -t$'\t' -k1,1rn -k3,3)"
if [[ "$LIMIT" -gt 0 ]]; then
  sorted="$(printf '%s\n' "$sorted" | head -n "$LIMIT")"
fi

printf '%s\n' "$sorted" | while IFS=$'\t' read -r since last doc; do
  [[ -z "${doc:-}" ]] && continue
  printf '%-14s  %-12s  %s\n' "$since" "$last" "$doc"
done

echo
echo "Tracked docs: ${#docs[@]}"

if [[ "$INCLUDE_UNTRACKED" -eq 1 ]]; then
  mapfile -t untracked < <(git -C "$TARGET" ls-files --others --exclude-standard -- '*.md' '*.mdx' | sort)
  echo
  if [[ ${#untracked[@]} -eq 0 ]]; then
    echo "Untracked docs: none."
  else
    echo "Untracked docs (${#untracked[@]}) — never reviewed through a PR:"
    printf '  %s\n' "${untracked[@]}"
  fi
fi

echo
echo "CODE-COMMITS SINCE = commits touching non-doc files since this doc last changed."
echo "It ranks where to look first. It does not mean the doc is wrong — or right."
