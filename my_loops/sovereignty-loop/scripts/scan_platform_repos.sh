#!/usr/bin/env bash
# scan_platform_repos.sh <dep-name> [keyword ...] --repos <repo1,repo2,...>
#
# Surfaces candidate hits for one external dependency across a set of
# platform repos. Each --repos entry can be a local path (used as-is) or an
# owner/repo slug (shallow-cloned into a scratch dir if not already checked
# out locally). A bare repo name (no "/") is tried against BOTH namespaces —
# Rusty-Mill/<name> then baileyrd/<name> — since org migration from the
# personal namespace isn't complete; see references/platform-directory.md
# for which namespace a given repo is actually in. Prints
# "<repo>:<file>:<line>: <matched text>" per hit, grouped by repo — a
# candidate list to read and judge, not a verdict.
#
# Requires: ripgrep (rg) if present, falls back to grep -rn. gh + git only
# needed for the owner/repo-slug clone path.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: scan_platform_repos.sh <dep-name> [keyword ...] --repos <repo1,repo2,...>" >&2
  exit 2
fi

DEP=""
KEYWORDS=()
REPOS=()
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repos)
      IFS=',' read -ra REPOS <<< "$2"; shift 2 ;;
    *)
      if [[ -z "$DEP" ]]; then DEP="$1"; else KEYWORDS+=("$1"); fi
      shift ;;
  esac
done

if [[ -z "$DEP" || ${#REPOS[@]} -eq 0 ]]; then
  echo "Need a dependency name and --repos <list>" >&2
  exit 2
fi

TERMS=("$DEP" "${KEYWORDS[@]}")
PATTERN="$(IFS='|'; echo "${TERMS[*]}")"

search() {
  local dir="$1" label="$2"
  if command -v rg >/dev/null 2>&1; then
    rg -n -i -e "$PATTERN" "$dir" --type rust --type toml --type markdown \
      2>/dev/null | sed "s|^|$label: |" || true
  else
    grep -rniE "$PATTERN" "$dir" --include='*.rs' --include='*.toml' --include='*.md' \
      2>/dev/null | sed "s|^|$label: |" || true
  fi
}

for repo in "${REPOS[@]}"; do
  if [[ -d "$repo" ]]; then
    search "$repo" "$repo"
    continue
  fi
  if [[ "$repo" == */* ]]; then
    dest="$SCRATCH/$(basename "$repo")"
    if gh repo clone "$repo" "$dest" -- --depth 1 >/dev/null 2>&1; then
      search "$dest" "$repo"
    else
      echo "# could not access '$repo' (not a local path, clone failed) — skipped" >&2
    fi
    continue
  fi
  # bare repo name, e.g. "rusty_json" — try Rusty-Mill first, then baileyrd
  dest="$SCRATCH/$repo"
  if gh repo clone "Rusty-Mill/$repo" "$dest" -- --depth 1 >/dev/null 2>&1; then
    search "$dest" "Rusty-Mill/$repo"
  elif gh repo clone "baileyrd/$repo" "$dest" -- --depth 1 >/dev/null 2>&1; then
    search "$dest" "baileyrd/$repo"
  else
    echo "# could not access '$repo' under Rusty-Mill/ or baileyrd/ — skipped" >&2
  fi
done
