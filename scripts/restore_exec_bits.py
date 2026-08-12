#!/usr/bin/env python3
"""Restore git executable bits lost when files are moved/copied without `git mv`.

This repo runs with `core.fileMode=false` and is worked on from Windows, so
`git add` never derives the executable bit from the OS -- a new or
moved/copied file always lands in the index as 100644, even if the exact
same content was 100755 at HEAD. That's what happened to
`repo-config/scripts/apply.sh` and `audit.sh` once already (see
`repo-config/RELEASE_NOTES.md`), fixed by hand with
`git update-index --chmod=+x`. This script does that match-and-fix
automatically, matched by git blob sha (content), not by path, so it
survives renames and directory reshuffles like the my_loops/ regroup.

Must run after `git add` (it inspects the staged index). Safe to run
repeatedly -- a no-op once nothing has drifted.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout


def executable_blobs_at_head() -> set[str]:
    """Blob shas that were mode 100755 anywhere in HEAD's tree."""
    blobs = set()
    try:
        listing = _git("ls-tree", "-r", "HEAD")
    except subprocess.CalledProcessError:
        return blobs  # no commits yet
    for line in listing.splitlines():
        meta, _, _path = line.partition("\t")
        mode, _kind, sha = meta.split()
        if mode == "100755":
            blobs.add(sha)
    return blobs


def restore(dry_run: bool = False) -> list[str]:
    """Re-mark staged 100644 files +x if their content was 100755 at HEAD."""
    exec_blobs = executable_blobs_at_head()
    if not exec_blobs:
        return []
    fixed = []
    try:
        staged = _git("ls-files", "-s")
    except subprocess.CalledProcessError:
        return []
    for line in staged.splitlines():
        meta, _, path = line.partition("\t")
        mode, sha, _stage = meta.split()
        if mode == "100644" and sha in exec_blobs:
            fixed.append(path)
            if not dry_run:
                _git("update-index", "--chmod=+x", "--", path)
    return fixed


def main() -> int:
    dry_run = "--dry-run" in sys.argv[1:]
    fixed = restore(dry_run=dry_run)
    if not fixed:
        print("No executable bits to restore.")
        return 0
    verb = "Would restore" if dry_run else "Restored"
    for path in fixed:
        print(f"{verb} +x: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
