#!/usr/bin/env python3
"""Restore git executable bits that `git add` can't derive on this repo.

This repo runs with `core.fileMode=false` and is worked on from Windows, so
`git add` never derives the executable bit from the OS -- a new or
moved/copied file always lands in the index as 100644, even if the exact
same content was 100755 at HEAD. That's what happened to
`repo-config/scripts/apply.sh` and `audit.sh` once already (see
`repo-config/RELEASE_NOTES.md`), fixed by hand with
`git update-index --chmod=+x`.

Two independent signals decide whether a staged 100644 file should be +x,
matching `build_skill_zips.py`'s precedence exactly:

1. **A shebang.** Decisive on its own, and tied to nothing external: a file
   starting with `#!` is meant to be run directly. This catches a
   *genuinely new* script, which signal 2 cannot -- a brand-new file has no
   prior blob to match, so for the first year of this repo every new script
   silently shipped non-executable unless someone remembered `chmod +x`
   before `git add`. 18 tracked scripts were in that state when this check
   was added.
2. **Content that was 100755 at HEAD.** Matched by git blob sha, not by
   path, so it survives renames and directory reshuffles like the my_loops/
   regroup. This is the original check and still the only one that helps an
   executable with no shebang (a committed binary, say).

The shebang is read from the *staged blob*, not the working-tree file --
what's about to be committed is what matters, and the two can differ.

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


def _git_bytes(*args: str) -> bytes:
    """Undecoded git output, for blob content that may not be text."""
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, check=True
    ).stdout


def blob_has_shebang(sha: str) -> bool:
    """True if the staged blob `sha` starts with `#!`.

    One `git cat-file` per candidate file. A batched `--batch` read would be
    one subprocess instead of N, at the cost of hand-parsing binary-safe
    length-prefixed output -- not worth it for a hand-run script on a repo
    this size."""
    try:
        return _git_bytes("cat-file", "blob", sha)[:2] == b"#!"
    except subprocess.CalledProcessError:
        return False


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


def chmod_worktree(path: Path) -> None:
    """Mirror the index fix onto the file on disk, where the OS tracks modes.

    Without this, a clone with `core.fileMode=true` (any Linux/macOS
    checkout) ends up with the index saying 100755 and the file on disk
    saying 644 -- which git reports as an unstaged
    `old mode 100755 / new mode 100644` change, and which the documented
    `git add -A` workflow then silently reverts. Windows is a no-op here;
    there's no bit on disk to mirror."""
    try:
        mode = path.stat().st_mode
    except OSError:
        return  # staged deletion, or otherwise not on disk -- index fix stands
    # +x wherever +r already is, so the file stays as (un)readable as it was.
    path.chmod(mode | ((mode & 0o444) >> 2))


def restore(dry_run: bool = False) -> list[str]:
    """Re-mark staged 100644 files +x when either signal says they're runnable.

    Note there's no `if not exec_blobs: return []` short-circuit any more --
    the shebang check stands on its own, so a repo with no commits yet (or
    none with an executable in HEAD) is still worth scanning."""
    exec_blobs = executable_blobs_at_head()
    fixed = []
    try:
        staged = _git("ls-files", "-s")
    except subprocess.CalledProcessError:
        return []
    for line in staged.splitlines():
        meta, _, path = line.partition("\t")
        mode, sha, _stage = meta.split()
        if mode != "100644":
            continue
        if sha in exec_blobs or blob_has_shebang(sha):
            fixed.append(path)
            if not dry_run:
                _git("update-index", "--chmod=+x", "--", path)
                chmod_worktree(REPO_ROOT / path)
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
