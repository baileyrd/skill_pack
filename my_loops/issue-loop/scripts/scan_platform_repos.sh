#!/usr/bin/env bash
# scan_platform_repos.sh <symbol-or-capability> [keyword ...] --repos <repo1,repo2,...>
#
# Surfaces candidate hits for one issue across platform repos — used before
# implementing to check whether an existing implementation could be ported
# instead of writing one from scratch. Each --repos entry can be a local
# path (used as-is) or an owner/repo slug (shallow-cloned into scratch if
# not already checked out locally). A bare repo name (no "/") is tried
# against BOTH namespaces — Rusty-Mill/<name> and baileyrd/<name> — since
# org migration from the personal namespace isn't complete; see
# references/platform-directory.md for which namespace a given repo is
# actually in. Prints "<repo>:<file>:<line>: <matched text>" per hit,
# grouped by repo — a candidate list to read and judge, not a verdict.
#
# Requires: ripgrep (rg) if present, falls back to grep -rn. gh + git only
# needed for the owner/repo-slug clone path.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: scan_platform_repos.sh <symbol-or-capability> [keyword ...] --repos <repo1,repo2,...>" >&2
  exit 2
fi

TARGET=""
KEYWORDS=()
REPOS=()
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repos)
      IFS=',' read -ra REPOS <<< "$2"; shift 2 ;;
    *)
      if [[ -z "$TARGET" ]]; then TARGET="$1"; else KEYWORDS+=("$1"); fi
      shift ;;
  esac
done

if [[ -z "$TARGET" || ${#REPOS[@]} -eq 0 ]]; then
  echo "Need a symbol/capability name and --repos <list>" >&2
  exit 2
fi

TERMS=("$TARGET" "${KEYWORDS[@]}")
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

try_clone() {
  local slug="$1" dest="$2"
  gh repo clone "$slug" "$dest" -- --depth 1 >/dev/null 2>&1
}

for repo in "${REPOS[@]}"; do
  if [[ -d "$repo" ]]; then
    search "$repo" "$repo"
    continue
  fi
  if [[ "$repo" == */* ]]; then
    dest="$SCRATCH/$(basename "$repo")"
    if try_clone "$repo" "$dest"; then
      search "$dest" "$repo"
    else
      echo "# could not access '$repo' (not a local path, clone failed) — skipped" >&2
    fi
    continue
  fi
  # bare repo name — try Rusty-Mill first, then baileyrd, per the widened
  # directory's two namespaces
  dest="$SCRATCH/$repo"
  if try_clone "Rusty-Mill/$repo" "$dest"; then
    search "$dest" "Rusty-Mill/$repo"
  elif try_clone "baileyrd/$repo" "$dest"; then
    search "$dest" "baileyrd/$repo"
  else
    echo "# could not access '$repo' under Rusty-Mill/ or baileyrd/ — skipped" >&2
  fi
done
