#!/usr/bin/env bash
# index_capabilities.sh <repo-path> [--out <file>]
#
# Walks a repo's Rust source and extracts a flat capability index: one row
# per module (from its //! doc) and one row per public fn/struct/trait/enum
# (from its /// doc, if any). Mechanical extraction only — this is candidate
# material for find_clusters.py, not a judgment about what's duplicated.
#
# Output (TSV, no header): repo<TAB>file<TAB>item_kind<TAB>item_name<TAB>doc
# item_kind is "module" for file-level //! docs, else fn/struct/trait/enum.
#
# Requires: awk, find. No third-party dependency.

set -euo pipefail

REPO=""
OUT="/dev/stdout"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    *) REPO="$1"; shift ;;
  esac
done

if [[ -z "$REPO" || ! -d "$REPO" ]]; then
  echo "Usage: index_capabilities.sh <repo-path> [--out <file>]" >&2
  exit 2
fi

REPO_NAME="$(basename "$REPO")"

: > "$OUT" 2>/dev/null || true  # truncate if writing to a real file; ignore for /dev/stdout

find "$REPO" -type f -name '*.rs' -not -path '*/target/*' | while read -r f; do
  rel="${f#"$REPO"/}"

  # Module-level doc: leading //! lines at the top of the file, joined.
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
  ' "$f")"
  if [[ -n "$moddoc" ]]; then
    printf '%s\t%s\tmodule\t%s\t%s\n' "$REPO_NAME" "$rel" "$rel" "$moddoc" >> "$OUT"
  fi

  # Public items: /// doc directly above a pub fn/struct/trait/enum.
  awk -v repo="$REPO_NAME" -v file="$rel" '
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
      printf "%s\t%s\t%s\t%s\t%s\n", repo, file, kind, name, doc
      doc=""
      next
    }
    { doc="" }
  ' "$f" >> "$OUT"
done
