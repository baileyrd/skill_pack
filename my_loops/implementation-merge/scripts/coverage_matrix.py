#!/usr/bin/env python3
"""coverage_matrix.py <index1.tsv> [index2.tsv ...]

Groups capability-index rows (label, file, item_kind, item_name, doc) by a
normalized item name and prints EVERY item, one row per normalized name,
with which labels have it. Unlike dedupe-loop's/repo-inspector's
find_clusters.py, this does NOT filter to items appearing in >=2 sources —
a row present in only one candidate is exactly the information
implementation-merge step 2's comparison and step 4's "never silently drop"
check both need, so single-source rows are the point here, not noise to
discard.

Two uses of the same tool, by design:
  1. Run over just the candidates' own indices (step 2) to see what's
     shared, what's one-sided, and what conflicts (same name, different
     kind or divergent doc) before deciding mergeability.
  2. Run again over [candidates' indices + the proposed merge's own index]
     (step 4) to verify every original item resolved to either present in
     the merge or explicitly written up as dropped in MERGE-PROPOSAL.md —
     an item that's neither is the silent-drop this skill exists to catch.

Output (TSV): normalized_name<TAB>kind<TAB>labels_with_it(comma-sep)<TAB>labels_missing_it(comma-sep, blank if none)<TAB>doc_previews

Stdlib only, no third-party dependency, in keeping with the standing
minimal-dependencies principle.
"""
import sys
import re
from collections import defaultdict

# Same normalization as dedupe-loop's/repo-inspector's find_clusters.py, so
# the same item reads as the same item across all three tools.
_STRIP_PREFIXES = ("get_", "new_", "make_", "build_", "create_", "with_")
_STRIP_SUFFIXES = ("_impl", "_inner", "_v2", "_new")


def normalize(name: str) -> str:
    n = name.strip()
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
                label, file, kind, name, doc = parts
                rows.append((label, file, kind, name, doc))
    return rows


def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2

    rows = load_rows(argv)
    all_labels = sorted({r[0] for r in rows})
    if not all_labels:
        print("No rows in the given index/indices.", file=sys.stderr)
        return 0

    groups = defaultdict(list)
    for row in rows:
        label, file, kind, name, doc = row
        key = (kind, normalize(name))
        groups[key].append(row)

    print(f"# {len(all_labels)} label(s): {', '.join(all_labels)}", file=sys.stderr)

    for (kind, norm_name), entries in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        have = sorted({r[0] for r in entries})
        missing = [l for l in all_labels if l not in have]
        doc_previews = []
        for label, file, item_kind, name, doc in entries:
            preview = (doc[:60] + "…") if len(doc) > 60 else doc
            doc_previews.append(f"{label}:{name}={preview}")
        row_out = [
            norm_name,
            kind,
            ",".join(have),
            ",".join(missing),
            " | ".join(doc_previews),
        ]
        print("\t".join(row_out))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
