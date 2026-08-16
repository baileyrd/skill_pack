#!/usr/bin/env python3
"""Install/update every skill in this repo into Claude Code's skills directory.

Claude Code discovers skills at ``~/.claude/skills/<name>/SKILL.md``. OMP's
own `claude` discovery provider (priority 80) reads that exact same tree
automatically, so this one sync target covers Claude Code and OMP together
-- no separate OMP install step needed.

claude.ai and Claude Desktop have no scriptable install path (ZIP upload
through their own Settings UI only, per current docs) and are deliberately
out of scope here.

For each skill directory (see build_skill_zips.find_skill_dirs), mirrors its
contents into ``<target>/<skill-name>/``: adds new files, updates changed
ones, and removes files no longer present in the source -- a real
install-or-update-or-replace, not an additive copy. File modes come from the
git index, same rationale as build_skill_zips.py / restore_exec_bits.py.

Source files are enumerated by build_skill_zips.iter_skill_files, so an
install and a zip contain exactly the same thing. Because build artifacts
are now absent from the source set, the stale-file pass removes any
``__pycache__`` an earlier version of this script already installed -- no
manual cleanup needed.

Usage:
    python scripts/install_skills.py [--dry-run] [--target DIR]
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_skill_zips import (  # noqa: E402
    REPO_ROOT,
    find_skill_dirs,
    git_file_mode,
    iter_skill_files,
)
from restore_exec_bits import restore as restore_exec_bits  # noqa: E402

DEFAULT_TARGET = Path.home() / ".claude" / "skills"


def sync_skill(skill_dir: Path, dest_dir: Path, dry_run: bool) -> tuple[int, int, int]:
    """Mirror `skill_dir` into `dest_dir`. Returns (added, updated, removed)."""
    src_files = {p.relative_to(skill_dir) for p in iter_skill_files(skill_dir)}
    dest_files = (
        {p.relative_to(dest_dir) for p in dest_dir.rglob("*") if p.is_file()}
        if dest_dir.exists()
        else set()
    )

    added = updated = 0
    for rel in sorted(src_files):
        src = skill_dir / rel
        dst = dest_dir / rel
        is_new = rel not in dest_files
        changed = is_new or not filecmp.cmp(src, dst, shallow=False)
        if not changed:
            continue
        added += is_new
        updated += not is_new
        if dry_run:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        dst.chmod(git_file_mode(REPO_ROOT, src))

    stale = dest_files - src_files
    if not dry_run:
        for rel in stale:
            (dest_dir / rel).unlink()
        # prune directories left empty by removals, deepest first
        if dest_dir.exists():
            for d in sorted((p for p in dest_dir.rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)):
                if not any(d.iterdir()):
                    d.rmdir()

    return added, updated, len(stale)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report planned changes without writing")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET, help="skills directory to install into")
    args = parser.parse_args()

    for path in restore_exec_bits(dry_run=args.dry_run):
        print(f"{'Would restore' if args.dry_run else 'Restored'} +x: {path}")

    skill_dirs = find_skill_dirs(REPO_ROOT)
    if not skill_dirs:
        print("No SKILL.md files found under", REPO_ROOT, file=sys.stderr)
        return 1

    if not args.dry_run:
        args.target.mkdir(parents=True, exist_ok=True)

    verb = "Would sync" if args.dry_run else "Synced"
    for skill_dir in skill_dirs:
        dest = args.target / skill_dir.name
        added, updated, removed = sync_skill(skill_dir, dest, args.dry_run)
        print(f"{verb} {skill_dir.name}: +{added} added, ~{updated} updated, -{removed} removed -> {dest}")

    print(f"\n{len(skill_dirs)} skill(s) synced into {args.target}")
    print("OMP's `claude` discovery provider reads this same directory automatically.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
