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

# Templates that land as dotfiles are STORED under a `dot-` prefix
# (`dot-gitattributes`, `dot-github/...`) and get their real name back here.
#
# This is deliberate and load-bearing — do not "tidy" the names back. The sync
# that delivers this skill to a session copies with a glob that doesn't match
# dot-prefixed entries, so every one of them was silently missing from the
# delivered copy: .gitattributes, both issue/PR template trees, and both CI
# workflows (issue #41). apply.sh cannot write a template that isn't there, so
# a target repo could not reach 11/11 and the operator had to hand-write the
# gap. The sync lives outside this repo; not depending on it does not.
#
# tests/test_no_dotfiles_in_assets.py enforces the convention repo-wide.
undot() {
  local path="$1" out="" seg
  local IFS=/
  for seg in $path; do
    [[ "$seg" == dot-* ]] && seg=".${seg#dot-}"
    out="${out:+$out/}$seg"
  done
  printf '%s' "$out"
}

copy_one() {
  local src="$1" rel="$2"
  local dest="$TARGET_DIR/$rel"
  mkdir -p "$(dirname "$dest")"
  if [[ -f "$dest" && "$FORCE" != true ]]; then
    echo "skip   $rel (already exists — use --force to overwrite)"
    skipped=$((skipped + 1))
    return
  fi
  # A missing template is a hard error, not a line of sed noise. The shell
  # creates "$dest" for the redirect BEFORE sed runs, so a failed sed leaves a
  # zero-byte file behind — and a zero-byte .github/workflows/*.yml is invalid
  # to GitHub and reported red on every push. One was committed and merged into
  # a real repo this way (issue #40).
  if [[ ! -f "$src" ]]; then
    echo "ERROR  $rel — template missing at $src" >&2
    echo "       Refusing to write a partial file. This usually means the synced" >&2
    echo "       copy of this skill is incomplete (see issue #41)." >&2
    exit 1
  fi
  # Write via a temp file and mv on success, so a failed substitution can never
  # leave a partial or empty destination behind.
  local tmp
  tmp="$(mktemp "${dest}.XXXXXX")"
  if ! sed -e "s#{{OWNER_REPO}}#$OWNER_REPO#g" \
           -e "s#{{SECURITY_CONTACT}}#$SECURITY_CONTACT#g" \
           "$src" > "$tmp"; then
    rm -f "$tmp"
    echo "ERROR  $rel — substitution failed, destination left untouched" >&2
    exit 1
  fi
  mv "$tmp" "$dest"
  echo "write  $rel"
  created=$((created + 1))
}

# Copy everything EXCEPT the CI workflows — those are stack-selected below, not
# copied blanket (a Rust repo must not get a Python workflow that fails every run).
while IFS= read -r -d '' f; do
  rel="$(undot "${f#"$TEMPLATES_DIR"/}")"
  [[ "$rel" == .github/workflows/* ]] && continue
  copy_one "$f" "$rel"
done < <(find "$TEMPLATES_DIR" -type f -print0)

# CI workflow selection, driven by which manifests the target actually has.
# A polyglot repo legitimately gets both. A repo with neither manifest gets none —
# there's nothing for CI to run yet, and an always-red workflow is worse than none.
#
# Before selecting anything: if the target already has ANY non-empty workflow,
# leave CI alone. The non-destructive skip in copy_one only protects a file at
# the *same path* — it cannot know that a differently-named file already does
# the job. A real repo with a tuned `ci.yml` (disk-reclaim steps, a scoped
# Windows job, schema-drift and plugin-version checks) would otherwise get a
# stock `ci-rust.yml` dropped alongside it, re-adding the very file that repo's
# merge had just folded in, and ending with two overlapping gates (issue #42).
# SKILL.md's own reason for including CI at all — "so the 'on green CI, merge'
# rule has a real check to gate on" — is already satisfied by any working
# workflow, whatever it is called.
# NB: this script runs under `set -euo pipefail`, so `find` on a non-existent
# directory would abort the whole run — and a target with no .github/workflows
# yet is the *common* case, not an edge one. Guard on the directory first and
# swallow a non-zero exit explicitly.
existing_ci=""
if [[ -d "$TARGET_DIR/.github/workflows" ]]; then
  existing_ci="$(find "$TARGET_DIR/.github/workflows" -maxdepth 1 \
                   \( -name '*.yml' -o -name '*.yaml' \) -size +0 2>/dev/null \
                 | head -n 3 | xargs -r -n1 basename | paste -sd, - || true)"
fi
if [[ -n "$existing_ci" ]]; then
  echo "skip   .github/workflows/ — target already has a workflow ($existing_ci);"
  echo "       not adding a second, overlapping gate. Review it by hand if the"
  echo "       existing one doesn't actually gate merges."
  skipped=$((skipped + 1))
  ci_selected=-1
fi

ci_selected=${ci_selected:-0}
if [[ "$ci_selected" -ge 0 ]] && [[ -f "$TARGET_DIR/Cargo.toml" ]]; then
  copy_one "$TEMPLATES_DIR/dot-github/workflows/ci-rust.yml" ".github/workflows/ci-rust.yml"
  ci_selected=$((ci_selected + 1))
fi
if [[ "$ci_selected" -ge 0 ]] && [[ -f "$TARGET_DIR/pyproject.toml" || -f "$TARGET_DIR/setup.py" ]]; then
  copy_one "$TEMPLATES_DIR/dot-github/workflows/ci-python.yml" ".github/workflows/ci-python.yml"
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
