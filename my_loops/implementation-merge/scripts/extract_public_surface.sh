#!/usr/bin/env bash
# extract_public_surface.sh <label>=<path> [<label>=<path> ...] [--out <file>]
#
# Extracts a flat capability index from N explicitly-named candidates —
# each a Rust source file or a directory (walked recursively) — tagged by
# the caller's own label rather than a repo/crate name. Same extraction as
# repo-inspector's index_workspace_capabilities.sh (module-level `//!` docs,
# `pub fn`/`pub struct`/`pub trait`/`pub enum` with their `///` doc), scoped
# down to an explicit candidate list instead of a whole workspace, since
# this skill operates on one already-identified cluster (handed in by
# repo-inspector/dedupe-loop, or named directly), not a scan target.
#
# Output (TSV, no header): label<TAB>file<TAB>item_kind<TAB>item_name<TAB>doc
# `file` is relative to the candidate's own path if a directory, or just the
# basename if a single file.
#
# This is candidate material for coverage_matrix.py, not a judgment about
# what's mergeable — read the actual source before deciding.
#
# Requires: awk, find. No third-party dependency.

set -euo pipefail

OUT="/dev/stdout"
declare -a PAIRS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    *) PAIRS+=("$1"); shift ;;
  esac
done

if [[ ${#PAIRS[@]} -eq 0 ]]; then
  echo "Usage: extract_public_surface.sh <label>=<path> [<label>=<path> ...] [--out <file>]" >&2
  exit 2
fi

: > "$OUT" 2>/dev/null || true  # truncate if writing to a real file; ignore for /dev/stdout

extract_one() {
  local LABEL="$1" FILE="$2" REL="$3"

  local moddoc
  moddoc="$(awk '
    /^[[:space:]]*\/\/!/ {
      line=$0
      sub(/^[[:space:]]*\/\/![[:space:]]?/, "", line)
      doc = (doc=="") ? line : doc" "line
      next
    }
    /^[[:space:]]*$/ { next }
    { exit }
    END { print doc }
  ' "$FILE")"
  if [[ -n "$moddoc" ]]; then
    printf '%s\t%s\tmodule\t%s\t%s\n' "$LABEL" "$REL" "$REL" "$moddoc" >> "$OUT"
  fi

  awk -v label="$LABEL" -v file="$REL" '
    /^[[:space:]]*\/\/\// {
      line=$0
      sub(/^[[:space:]]*\/\/\/[[:space:]]?/, "", line)
      doc = (doc=="") ? line : doc" "line
      next
    }
    /^[[:space:]]*#\[/ { next }
    /^[[:space:]]*$/ { next }
    /^[[:space:]]*pub[[:space:]]+(fn|struct|trait|enum)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*/ {
      s=$0
      match(s, /pub[[:space:]]+(fn|struct|trait|enum)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*/)
      tok=substr(s, RSTART, RLENGTH)
      n=split(tok, parts, /[[:space:]]+/)
      kind=parts[2]
      name=parts[3]
      gsub(/[<(:].*/, "", name)
      printf "%s\t%s\t%s\t%s\t%s\n", label, file, kind, name, doc
      doc=""
      next
    }
    { doc="" }
  ' "$FILE" >> "$OUT"
}

for pair in "${PAIRS[@]}"; do
  LABEL="${pair%%=*}"
  PATH_ARG="${pair#*=}"
  if [[ -z "$LABEL" || "$LABEL" == "$pair" || -z "$PATH_ARG" ]]; then
    echo "Bad argument '$pair' — expected <label>=<path>" >&2
    exit 2
  fi
  if [[ -f "$PATH_ARG" ]]; then
    extract_one "$LABEL" "$PATH_ARG" "$(basename "$PATH_ARG")"
  elif [[ -d "$PATH_ARG" ]]; then
    find "$PATH_ARG" -type f -name '*.rs' -not -path '*/target/*' | while read -r f; do
      rel="${f#"$PATH_ARG"/}"
      extract_one "$LABEL" "$f" "$rel"
    done
  else
    echo "'$PATH_ARG' (label '$LABEL') is neither a file nor a directory — skipped" >&2
  fi
done
