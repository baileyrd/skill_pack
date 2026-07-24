#!/usr/bin/env python3
"""find_clusters.py <index1.tsv> [index2.tsv ...]

Groups capability-index rows (repo, file, item_kind, item_name, doc) by a
normalized item name and prints clusters that span two or more distinct
repos. This is candidate surfacing, not classification — read the actual
source for each hit before deciding exact-duplicate / convergent-but-
diverged / coincidental-similarity (dedupe-loop's step 2).

Stdlib only, no third-party dependency, in keeping with the standing
minimal-dependencies principle.
"""
import sys
import re
from collections import defaultdict

# Common affixes that don't change what a thing IS, only how it's named.
_STRIP_PREFIXES = ("get_", "new_", "make_", "build_", "create_", "with_")
_STRIP_SUFFIXES = ("_impl", "_inner", "_v2", "_new")


def normalize(name: str) -> str:
    n = name.strip()
    # snake_case and CamelCase both fold to lowercase-with-underscores
    n = re.sub(r"(?<!^)(?=[A-Z])", "_", n).lower()
    n = re.sub(r"_+", "_", n).strip("_")
    changed = True
    while changed:
        changed = False
        for p in _STRIP_PREFIXES:
            if n.startswith(p):
                n = n[len(p):]
                changed = True
        for s in _STRIP_SUFFIXES:
            if n.endswith(s):
                n = n[: -len(s)]
                changed = True
    return n


def load_rows(paths):
    rows = []
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) != 5:
                    continue
                repo, file, kind, name, doc = parts
                rows.append((repo, file, kind, name, doc))
    return rows


def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2

    rows = load_rows(argv)
    clusters = defaultdict(list)
    for row in rows:
        repo, file, kind, name, doc = row
        key = (kind, normalize(name))
        clusters[key].append(row)

    candidates = {
        key: entries
        for key, entries in clusters.items()
        if len({r[0] for r in entries}) >= 2
    }

    if not candidates:
        print("No cross-repo candidates found in the given indices.")
        return 0

    for (kind, norm_name), entries in sorted(
        candidates.items(), key=lambda kv: -len({r[0] for r in kv[1]})
    ):
        repos = sorted({r[0] for r in entries})
        print(f"=== {kind}: {norm_name}  ({len(repos)} repos: {', '.join(repos)}) ===")
        for repo, file, item_kind, name, doc in entries:
            doc_preview = (doc[:80] + "…") if len(doc) > 80 else doc
            print(f"  {repo}:{file}  {name}  — {doc_preview}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
