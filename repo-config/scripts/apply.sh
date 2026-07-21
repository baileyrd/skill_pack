#!/usr/bin/env bash
# Copies assets/templates/ into a target repo, substituting {{OWNER_REPO}} and
# {{SECURITY_CONTACT}}. Non-destructive by default — existing files are skipped
# and reported; --force overwrites.
#
# Usage:
#   ./apply.sh /path/to/target-repo [--config config.env] [--force]
#
# Config file (optional) is simple shell-sourceable KEY=VALUE, e.g.:
#   OWNER_REPO=acme-org/widget-service
#   SECURITY_CONTACT=platform-team@acme.internal
#
# Resolution order for each token: --config value > `git remote` (OWNER_REPO only)
# > greenfield placeholder.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATES_DIR="$SOURCE_DIR/assets/templates"

TARGET_DIR="${1:-}"
shift || true

CONFIG_FILE=""
FORCE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG_FILE="$2"; shift 2 ;;
    --force) FORCE=true; shift ;;
    *) shift ;;
  esac
done

if [[ -z "$TARGET_DIR" || ! -d "$TARGET_DIR" ]]; then
  echo "Usage: $0 /path/to/target-repo [--config <file>] [--force]" >&2
  exit 1
fi

OWNER_REPO=""
SECURITY_CONTACT=""

if [[ -n "$CONFIG_FILE" && -f "$CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
fi

if [[ -z "${OWNER_REPO:-}" ]]; then
  remote_url="$(git -C "$TARGET_DIR" remote get-url origin 2>/dev/null || true)"
  if [[ -n "$remote_url" ]]; then
    remote_url="${remote_url%.git}"
    OWNER_REPO="$(echo "$remote_url" | sed -E 's#.*[:/]([^/:]+)/([^/:]+)$#\1/\2#')"
  fi
fi

OWNER_REPO="${OWNER_REPO:-<fill in once a git remote is set>}"
SECURITY_CONTACT="${SECURITY_CONTACT:-<fill in — team alias or individual>}"

created=0
skipped=0

copy_one() {
  local src="$1" rel="$2"
  local dest="$TARGET_DIR/$rel"
  mkdir -p "$(dirname "$dest")"
  if [[ -f "$dest" && "$FORCE" != true ]]; then
    echo "skip   $rel (already exists — use --force to overwrite)"
    skipped=$((skipped + 1))
    return
  fi
  sed -e "s#{{OWNER_REPO}}#$OWNER_REPO#g" \
      -e "s#{{SECURITY_CONTACT}}#$SECURITY_CONTACT#g" \
      "$src" > "$dest"
  echo "write  $rel"
  created=$((created + 1))
}

# Copy everything EXCEPT the CI workflows — those are stack-selected below, not
# copied blanket (a Rust repo must not get a Python workflow that fails every run).
while IFS= read -r -d '' f; do
  rel="${f#"$TEMPLATES_DIR"/}"
  [[ "$rel" == .github/workflows/* ]] && continue
  copy_one "$f" "$rel"
done < <(find "$TEMPLATES_DIR" -type f -print0)

# CI workflow selection, driven by which manifests the target actually has.
# A polyglot repo legitimately gets both. A repo with neither manifest gets none —
# there's nothing for CI to run yet, and an always-red workflow is worse than none.
ci_selected=0
if [[ -f "$TARGET_DIR/Cargo.toml" ]]; then
  copy_one "$TEMPLATES_DIR/.github/workflows/ci-rust.yml" ".github/workflows/ci-rust.yml"
  ci_selected=$((ci_selected + 1))
fi
if [[ -f "$TARGET_DIR/pyproject.toml" || -f "$TARGET_DIR/setup.py" ]]; then
  copy_one "$TEMPLATES_DIR/.github/workflows/ci-python.yml" ".github/workflows/ci-python.yml"
  ci_selected=$((ci_selected + 1))
fi
if [[ "$ci_selected" -eq 0 ]]; then
  echo "note   no Cargo.toml/pyproject.toml found — skipped CI workflows (nothing to run yet)"
fi

echo
echo "OWNER_REPO used: $OWNER_REPO"
echo "SECURITY_CONTACT used: $SECURITY_CONTACT"
echo "Done: $created written, $skipped skipped."
[[ "$FORCE" != true && "$skipped" -gt 0 ]] && echo "Re-run with --force to overwrite skipped files."
exit 0
