#!/usr/bin/env bash
# Gap checklist against the repo-config standard file set.
#
# Usage: audit.sh [target-dir]

set -euo pipefail

TARGET="${1:-.}"

if [[ ! -d "$TARGET" ]]; then
  echo "Usage: $0 [target-dir]" >&2
  exit 1
fi

# path|label — directories are satisfied by containing at least one file
items=(
  ".github/PULL_REQUEST_TEMPLATE|PR templates"
  ".github/ISSUE_TEMPLATE|Issue templates"
  "README.md|README"
  "CONTRIBUTING.md|CONTRIBUTING"
  "CODE_OF_CONDUCT.md|CODE_OF_CONDUCT"
  "SECURITY.md|SECURITY"
  "CHANGELOG.md|CHANGELOG"
  "RELEASE_NOTES.md|RELEASE_NOTES"
  "ARCHITECTURE.md|ARCHITECTURE"
  "docs/adr|ADR log"
)

score=0
total=${#items[@]}

echo "repo-config audit: $TARGET"
echo

for entry in "${items[@]}"; do
  path="${entry%%|*}"
  label="${entry##*|}"
  full="$TARGET/$path"

  if [[ -d "$full" ]]; then
    if find "$full" -type f | grep -q .; then
      echo "[x] $label"
      score=$((score + 1))
    else
      echo "[ ] $label  (dir exists but empty — $path)"
    fi
  elif [[ -f "$full" ]]; then
    echo "[x] $label"
    score=$((score + 1))
  else
    echo "[ ] $label  (missing — $path)"
  fi
done

echo
echo "Score: $score/$total"
