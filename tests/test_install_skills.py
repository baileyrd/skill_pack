#!/usr/bin/env python3
"""Tests for the file set shared by build_skill_zips.py and install_skills.py.

The bug these name: the "what counts as part of a skill" filter lived only in
`build_skill_zips.py`, while `install_skills.py` mirrored `skill_dir.rglob("*")`
wholesale. So the zips were clean and the installed tree was not --
`install_skills.py` copied `__pycache__` into `~/.claude/skills/<name>/scripts/`
on every install that followed a `check_repo.py` run, which is the exact order
the README recommends. Two tools disagreeing about the contents of a skill is
the kind of drift a shared helper prevents and duplicated logic does not, so
these test the helper *and* the agreement.

Stdlib unittest, same rationale as tests/README.md.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"


def load_module(name: str):
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


bsz = load_module("build_skill_zips")
ins = load_module("install_skills")


class TestIterSkillFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.skill = Path(self.tmp.name) / "demo"
        (self.skill / "scripts").mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: demo\nversion: 1.0.0\n---\n")
        (self.skill / "scripts/run.sh").write_text("#!/bin/sh\n")

    def tearDown(self):
        self.tmp.cleanup()

    def names(self):
        return {str(p.relative_to(self.skill)) for p in bsz.iter_skill_files(self.skill)}

    def test_real_files_are_included(self):
        self.assertEqual(self.names(), {"SKILL.md", "scripts/run.sh"})

    def test_pycache_directory_is_excluded(self):
        """The bug: `check_repo.py` runs `check_references.py`, Python writes
        `scripts/__pycache__/`, and the next install copied it into the
        skills directory."""
        cache = self.skill / "scripts/__pycache__"
        cache.mkdir()
        (cache / "check_references.cpython-311.pyc").write_bytes(b"\x00")
        self.assertEqual(self.names(), {"SKILL.md", "scripts/run.sh"})

    def test_loose_pyc_is_excluded(self):
        (self.skill / "scripts/stray.pyc").write_bytes(b"\x00")
        self.assertNotIn("scripts/stray.pyc", self.names())

    def test_ds_store_is_excluded(self):
        (self.skill / ".DS_Store").write_bytes(b"\x00")
        self.assertNotIn(".DS_Store", self.names())

    def test_nested_directories_are_walked(self):
        deep = self.skill / "references/nested"
        deep.mkdir(parents=True)
        (deep / "notes.md").write_text("x\n")
        self.assertIn("references/nested/notes.md", self.names())


class TestInstallerUsesTheSharedFilter(unittest.TestCase):
    """install_skills.py must enumerate sources through the same helper, not
    its own rglob -- that divergence *was* the bug."""

    def test_installer_imports_the_shared_helper(self):
        self.assertIs(ins.iter_skill_files, bsz.iter_skill_files)

    def test_artifacts_are_not_installed_and_stale_ones_are_removed(self):
        # Inside REPO_ROOT: sync_skill resolves modes via git_file_mode, which
        # is repo-relative by design. A /tmp fixture would test a path no
        # caller uses.
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as tmp:
            root = Path(tmp)
            skill = root / "src"
            (skill / "scripts/__pycache__").mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: src\nversion: 1.0.0\n---\n")
            (skill / "scripts/run.sh").write_text("#!/bin/sh\n")
            (skill / "scripts/__pycache__/x.cpython-311.pyc").write_bytes(b"\x00")

            dest = root / "dest"
            # a __pycache__ an older version of the installer already wrote
            (dest / "scripts/__pycache__").mkdir(parents=True)
            (dest / "scripts/__pycache__/old.pyc").write_bytes(b"\x00")

            ins.sync_skill(skill, dest, dry_run=False)

            installed = {str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()}
            self.assertEqual(installed, {"SKILL.md", "scripts/run.sh"})
            self.assertFalse(
                (dest / "scripts/__pycache__").exists(),
                "stale __pycache__ should be pruned, not left behind",
            )


class TestZipAndInstallAgree(unittest.TestCase):
    def test_every_skill_has_one_file_set(self):
        """The invariant the shared helper exists to hold: what a zip contains
        and what an install writes are the same list, for every real skill."""
        for skill_dir in bsz.find_skill_dirs(REPO_ROOT):
            with self.subTest(skill=skill_dir.name):
                from_helper = {p.relative_to(skill_dir) for p in bsz.iter_skill_files(skill_dir)}
                self.assertNotEqual(from_helper, set(), "skill enumerated as empty")
                self.assertFalse(
                    {p for p in from_helper if "__pycache__" in p.parts or p.suffix == ".pyc"},
                    "build artifacts leaked into a real skill's file set",
                )


if __name__ == "__main__":
    unittest.main()
