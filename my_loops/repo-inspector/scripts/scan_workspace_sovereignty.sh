#!/usr/bin/env bash
# scan_workspace_sovereignty.sh <workspace-root> [--crate <name>]
#
# Ported from sovereignty-loop's dependency-detection logic (cargo metadata
# inventory + cross-repo grep for internal coverage), adapted to operate
# inside a single Cargo workspace instead of across a `PLATFORM_REPOS` list.
#
# Step 1 — inventory: `cargo metadata` for every workspace member's direct,
# non-dev/build, non-path (i.e. genuinely external) dependencies, aggregated
# by dependency name across the whole workspace (or narrowed to one crate
# with --crate). A dependency also satisfied by another *workspace member*
# (by registry name) is excluded here — that's intra-workspace, not external.
#
# Step 2 — cross-repo search, reduced to a local grep: sovereignty-loop's
# scan_platform_repos.sh clones sibling repos that aren't checked out; this
# workspace already has every sibling crate local under crates/, so no clone
# path is needed. Greps every OTHER crate's source/manifest/README for the
# dependency's name — a candidate list to read and judge (does that crate
# already wrap or replace this dependency?), not a verdict. Hits inside a
# crate that itself declares the dependency are excluded (by manifest
# directory, not by name, so nested member paths like
# crates/rusty_search/crates/rusty-search-core resolve correctly) — those
# are just the dependency's own usage, not evidence of internal coverage.
#
# Output: one "=== <dependency> (used by: <crates>) ===" block per external
# dependency, followed by its in-workspace grep hits (if any) from crates
# that do NOT themselves declare it. Surfacing only — step 3
# (repo-inspector's classification: covered / partial / no internal
# equivalent found) is a human-in-the-loop read of these hits plus
# references/platform-directory.md for equivalents not yet in this workspace.
#
# Requires: cargo, python3 (stdlib only). ripgrep if present, grep otherwise.

set -euo pipefail

WORKSPACE=""
ONLY_CRATE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --crate) ONLY_CRATE="$2"; shift 2 ;;
    *) WORKSPACE="$1"; shift ;;
  esac
done

if [[ -z "$WORKSPACE" || ! -f "$WORKSPACE/Cargo.toml" ]]; then
  echo "Usage: scan_workspace_sovereignty.sh <workspace-root> [--crate <name>]" >&2
  exit 2
fi

# --no-deps: packages[].dependencies reflects each manifest's declared
# dependencies regardless of --no-deps (it doesn't need the resolved graph),
# and skipping resolution avoids a slow, network-dependent full-graph solve
# on a workspace this size.
METADATA="$(cargo metadata --no-deps --format-version=1 --manifest-path "$WORKSPACE/Cargo.toml")"

# dependency<TAB>user-crates(comma-separated)
DEPS_TSV="$(echo "$METADATA" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
member_ids = set(data["workspace_members"])
members_by_id = {p["id"]: p for p in data["packages"] if p["id"] in member_ids}
member_names = {p["name"] for p in members_by_id.values()}

only = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None

# dependency name -> set of workspace crate names that pull it in directly,
# normal kind (not dev/build), not a path dependency, not another member.
deps = {}
for pkg in members_by_id.values():
    if only and pkg["name"] != only:
        continue
    for dep in pkg["dependencies"]:
        if dep.get("kind"):
            continue
        if dep.get("path"):
            continue
        if dep["name"] in member_names:
            continue
        deps.setdefault(dep["name"], set()).add(pkg["name"])

for name in sorted(deps):
    users = ",".join(sorted(deps[name]))
    print(name + "\t" + users)
' "$ONLY_CRATE")"

if [[ -z "$DEPS_TSV" ]]; then
  echo "No external (non-workspace, non-dev/build) dependencies found." >&2
  exit 0
fi

# crate-name<TAB>absolute-manifest-dir, for turning a user-crate list into
# real directories to exclude from the internal-coverage search.
DIRS_TSV="$(echo "$METADATA" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
member_ids = set(data["workspace_members"])
for pkg in data["packages"]:
    if pkg["id"] in member_ids:
        manifest_dir = pkg["manifest_path"].rsplit("/", 1)[0]
        print(pkg["name"] + "\t" + manifest_dir)
')"

crate_dir() {
  awk -F'\t' -v c="$1" '$1 == c { print $2; exit }' <<< "$DIRS_TSV"
}

search_internal() {
  local pattern="$1"
  shift
  local -a exclude_paths=("$@")
  local hits
  # Exclude Cargo.lock explicitly: ripgrep's `toml` type matches it by name
  # (`rg --type-list` lists `Cargo.lock` under `toml`), and a lockfile
  # reflects the *resolved transitive* graph, not a crate's own source — a
  # popular dependency like `serde` shows up in nearly every crate's
  # Cargo.lock regardless of whether that crate does anything with it,
  # which drowned real hits in lockfile noise during testing.
  if command -v rg >/dev/null 2>&1; then
    hits="$(rg -n -i -e "$pattern" "$WORKSPACE/crates" --type rust --type toml --type markdown \
      -g '!target' -g '!Cargo.lock' 2>/dev/null || true)"
  else
    hits="$(grep -rniE "$pattern" "$WORKSPACE/crates" --include='*.rs' --include='*.toml' --include='*.md' \
      --exclude='Cargo.lock' 2>/dev/null | grep -v '/target/' || true)"
  fi
  for dir in "${exclude_paths[@]}"; do
    [[ -z "$dir" ]] && continue
    hits="$(grep -vF "$dir/" <<< "$hits" || true)"
  done
  echo "$hits"
}

while IFS=$'\t' read -r DEP USERS; do
  [[ -z "$DEP" ]] && continue
  echo "=== $DEP (used by: $USERS) ==="
  exclude_paths=()
  IFS=',' read -ra USER_LIST <<< "$USERS"
  for u in "${USER_LIST[@]}"; do
    exclude_paths+=("$(crate_dir "$u")")
  done
  # Capture fully before slicing: piping a large result straight into `head`
  # closes the pipe early and SIGPIPEs the writer, which — under `set -o
  # pipefail` — aborted this loop after the very first (and most common)
  # dependency in testing. A here-string hands `head` already-written data
  # instead of a live pipe, so there's nothing left to SIGPIPE.
  hits="$(search_internal "$DEP" "${exclude_paths[@]}")"
  head -20 <<< "$hits"
  echo
done <<< "$DEPS_TSV"
