#!/usr/bin/env python3
"""Package every skill in this repo into an installable zip under ``zip/``.

A skill is any directory containing a ``SKILL.md`` file. Each one is zipped
per Anthropic's Skills API packaging rule: the zip's single top-level entry
must be the skill directory itself (``zip -r name.zip name/``), so the
archive can be uploaded as-is or unzipped straight into ``~/.claude/skills/``.

Before zipping, it restores any executable bits git lost on the reorg (see
`restore_exec_bits.py`), then reads file modes from the git index rather
than the filesystem -- this repo runs with ``core.fileMode=false`` and is
worked on from Windows, where the OS never reports a real Unix executable
bit.

Usage:
    python scripts/build_skill_zips.py
"""

from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from restore_exec_bits import restore as restore_exec_bits  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ZIP_DIR = REPO_ROOT / "zip"
SKIP_DIR_NAMES = {".git", "zip", "__pycache__"}
SKIP_FILE_SUFFIXES = {".pyc"}
SKIP_FILE_NAMES = {".DS_Store"}


def find_skill_dirs(root: Path) -> list[Path]:
    """Every directory containing a SKILL.md, skipping .git/ and zip/."""
    skills = []
    for skill_md in sorted(root.rglob("SKILL.md")):
        if SKIP_DIR_NAMES & set(skill_md.relative_to(root).parts):
            continue
        skills.append(skill_md.parent)
    return skills


def git_file_mode(repo_root: Path, path: Path) -> int:
    """Executable bit for `path` from the git index; defaults to non-exec.

    Falls back to 0o644 for files git doesn't know about yet (e.g. before
    `git add`), since core.fileMode=false makes the working-tree bit
    meaningless anyway.
    """
    rel = path.relative_to(repo_root).as_posix()
    result = subprocess.run(
        ["git", "ls-files", "-s", "--", rel],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    line = result.stdout.strip()
    if line:
        mode = int(line.split()[0], 8)
        if mode & 0o111:
            return 0o755
    return 0o644


_VERSION_RE = re.compile(r"^version:\s*(\S+)\s*$", re.MULTILINE)


def skill_version(skill_dir: Path) -> str | None:
    """`version:` field from a skill's SKILL.md frontmatter, if present."""
    frontmatter = skill_dir.joinpath("SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
    match = _VERSION_RE.search(frontmatter)
    return match.group(1) if match else None


def build_zip(skill_dir: Path, repo_root: Path, zip_dir: Path) -> Path:
    skill_name = skill_dir.name
    version = skill_version(skill_dir)
    filename = f"{skill_name}-v{version}.zip" if version else f"{skill_name}.zip"
    zip_path = zip_dir / filename
    files = [
        p
        for p in sorted(skill_dir.rglob("*"))
        if p.is_file()
        and p.name not in SKIP_FILE_NAMES
        and p.suffix not in SKIP_FILE_SUFFIXES
        and not SKIP_DIR_NAMES & set(p.relative_to(skill_dir).parts[:-1])
    ]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            arcname = Path(skill_name) / f.relative_to(skill_dir)
            info = zipfile.ZipInfo.from_file(f, arcname=arcname.as_posix())
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = git_file_mode(repo_root, f)
            info.external_attr = (mode | 0o100000) << 16  # regular file + perm bits
            with f.open("rb") as fh:
                zf.writestr(info, fh.read())

    return zip_path


def main() -> int:
    skill_dirs = find_skill_dirs(REPO_ROOT)
    if not skill_dirs:
        print("No SKILL.md files found under", REPO_ROOT, file=sys.stderr)
        return 1

    for path in restore_exec_bits():
        print(f"Restored +x: {path}")
    if ZIP_DIR.exists():
        for stale in ZIP_DIR.glob("*.zip"):
            stale.unlink()
    ZIP_DIR.mkdir(exist_ok=True)

    for skill_dir in skill_dirs:
        zip_path = build_zip(skill_dir, REPO_ROOT, ZIP_DIR)
        rel = skill_dir.relative_to(REPO_ROOT)
        print(f"{rel} -> {zip_path.relative_to(REPO_ROOT)}")

    print(f"\nBuilt {len(skill_dirs)} skill zip(s) in {ZIP_DIR.relative_to(REPO_ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
