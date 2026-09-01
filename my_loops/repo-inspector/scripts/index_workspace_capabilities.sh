#!/usr/bin/env bash
# index_workspace_capabilities.sh <workspace-root> [--out <file>]
#
# Walks every crate in one Cargo workspace and extracts a flat capability
# index: one row per module (from its //! doc) and one row per public
# fn/struct/trait/enum (from its /// doc, if any). Same mechanical
# extraction as dedupe-loop's index_capabilities.sh, adapted to tag each row
# by CRATE (a `cargo metadata` workspace member) instead of by repo, since
# this skill clusters duplication *within* one Cargo workspace rather than
# across separate checkouts.
#
# Output (TSV, no header): crate<TAB>file<TAB>item_kind<TAB>item_name<TAB>doc
# item_kind is "module" for file-level //! docs, else fn/struct/trait/enum.
# `file` is relative to the crate's own manifest directory, so two crates
# can each report e.g. "src/lib.rs" without colliding once grouped by crate.
#
# This is candidate material for find_clusters.py, not a judgment about what
# is duplicated.
#
# Requires: cargo (to enumerate workspace members via `cargo metadata`),
# python3 (stdlib only, to parse the JSON), awk, find.

set -euo pipefail

WORKSPACE=""
OUT="/dev/stdout"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    *) WORKSPACE="$1"; shift ;;
  esac
done

if [[ -z "$WORKSPACE" || ! -f "$WORKSPACE/Cargo.toml" ]]; then
  echo "Usage: index_workspace_capabilities.sh <workspace-root> [--out <file>]" >&2
  exit 2
fi

: > "$OUT" 2>/dev/null || true  # truncate if writing to a real file; ignore for /dev/stdout

# crate-name<TAB>absolute-manifest-dir, one line per workspace member.
members="$(cargo metadata --no-deps --format-version=1 --manifest-path "$WORKSPACE/Cargo.toml" \
  | python3 -c '
import json
import sys

data = json.load(sys.stdin)
member_ids = set(data["workspace_members"])
for pkg in data["packages"]:
    if pkg["id"] in member_ids:
        manifest_dir = pkg["manifest_path"].rsplit("/", 1)[0]
        print(pkg["name"] + "\t" + manifest_dir)
')"

while IFS=$'\t' read -r CRATE CRATE_DIR; do
  [[ -z "$CRATE" ]] && continue

  find "$CRATE_DIR" -type f -name '*.rs' -not -path '*/target/*' | while read -r f; do
    rel="${f#"$CRATE_DIR"/}"

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
      printf '%s\t%s\tmodule\t%s\t%s\n' "$CRATE" "$rel" "$rel" "$moddoc" >> "$OUT"
    fi

    # Public items: /// doc directly above a pub fn/struct/trait/enum.
    awk -v crate="$CRATE" -v file="$rel" '
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
        printf "%s\t%s\t%s\t%s\t%s\n", crate, file, kind, name, doc
        doc=""
        next
      }
      { doc="" }
    ' "$f" >> "$OUT"
  done
done <<< "$members"
