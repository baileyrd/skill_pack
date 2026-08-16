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
  ".gitattributes|.gitattributes"
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

# CI is stack-conditional, so it's reported separately from the core score rather
# than as a fixed checklist item: only expected when a manifest exists to test.
if [[ -f "$TARGET/Cargo.toml" || -f "$TARGET/pyproject.toml" || -f "$TARGET/setup.py" ]]; then
  if find "$TARGET/.github/workflows" -maxdepth 1 -name 'ci-*.yml' 2>/dev/null | grep -q .; then
    echo "[x] CI workflow (manifest present, workflow found)"
  else
    echo "[ ] CI workflow (manifest present but no .github/workflows/ci-*.yml — the"
    echo "    'on green CI, merge' rule has nothing to gate on)"
  fi
fi

# Presence != correctness, and .gitattributes is the one item where a present-but-
# wrong file leaves the exact problem it exists to prevent. A repo can carry a
# .gitattributes that only marks binaries and still hand out CRLF shell scripts.
if [[ -f "$TARGET/.gitattributes" ]] && ! grep -q 'eol=lf' "$TARGET/.gitattributes"; then
  echo
  echo "Note: .gitattributes is present but sets no 'eol=lf' — LF isn't enforced in"
  echo "      the working tree, so a Windows checkout can still produce CRLF scripts"
  echo "      that fail on their shebang. Presence alone doesn't fix that."
fi

# Presence != currency. Flag every log-shaped file that exists, not just one:
# naming RELEASE_NOTES.md alone implied it was the only file with this problem,
# and a run once reported a repo current while CHANGELOG.md had no record of the
# latest PR at all. Whether a log is up to date is a human/agent judgment either
# way; the script's job is to make sure none of them gets silently skipped.
for log in RELEASE_NOTES.md CHANGELOG.md; do
  [[ -f "$TARGET/$log" ]] || continue
  echo
  echo "Note: $log is present but this audit checks presence only —"
  echo "      confirm separately that its newest entry covers the latest change,"
  echo "      and that entries whose PRs have merged carry their links."
done
