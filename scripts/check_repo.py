#!/usr/bin/env python3
"""check_repo.py [--only NAME] — repo-wide lint for skill_pack.

Every check here exists because the thing it checks for actually went wrong
in this repo, was found by hand, and cost a PR to fix. This is not generic
hygiene: a check earns its place by naming the commit that would have failed
it.

  exec-bits   18 tracked scripts were committed 100644 despite starting with
              `#!`, so they shipped non-executable for months (PR #22).
  line-ends   The synced copy of repo-config's audit.sh arrived with CRLF and
              died on its own shebang (PR #20). The index was clean that time;
              this is the regression guard, not a re-fix.
  doc-refs    docs-loop's first run found a dead script path in dedupe-loop
              and a TOC anchor pointing at nothing in datastar-pro
              (issues #16/#17). Runs against a baseline so only NEW breakage
              fails — see docs-refs-baseline.tsv.
  manifests   Every skill needs `name` matching its directory, a semver
              `version`, and a RELEASE_NOTES.md. repo-config's own notes
              record a real fix shipping with no entry, caught only because
              the repo owner noticed.
  packaging   build_skill_zips.py runs clean — a smoke test that the tooling
              still works before anyone relies on its output.

Run it locally exactly as CI does:  python3 scripts/check_repo.py
Exit 0 if everything passes, 1 otherwise. Stdlib only.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE = REPO_ROOT / "docs-refs-baseline.tsv"
CHECK_REFERENCES = REPO_ROOT / "my_loops/docs-loop/scripts/check_references.py"

# The one skill exempt from the manifest rules: vendored from the
# third-party notebooklm-py package, carrying that package's version, never
# hand-edited here. Called out in README's Versioning section too.
VENDORED = {"yt_research_for_cc/notebooklm"}

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
BINARY_SUFFIXES = {".skill", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico"}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True, text=True, check=True,
    ).stdout


def git_bytes(*args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args], capture_output=True, check=True
    ).stdout


def staged_entries():
    """(mode, sha, path) for every tracked file."""
    for line in git("ls-files", "-s").splitlines():
        meta, _, path = line.partition("\t")
        mode, sha, _stage = meta.split()
        yield mode, sha, path


def check_exec_bits() -> list[str]:
    """A file starting with `#!` is meant to be run. Committed at 100644 it
    isn't, and on this repo `git add` can't derive the bit from the OS."""
    failures = []
    for mode, sha, path in staged_entries():
        if mode != "100644":
            continue
        if git_bytes("cat-file", "blob", sha)[:2] == b"#!":
            failures.append(f"{path} has a shebang but is mode 100644 (want 100755)")
    if failures:
        failures.append("fix: git add -A && python3 scripts/restore_exec_bits.py")
    return failures


def check_line_endings() -> list[str]:
    """CRLF in a committed text file breaks the shebang line on Linux/macOS.
    .gitattributes should prevent this ever reaching the index."""
    failures = []
    for _mode, sha, path in staged_entries():
        if Path(path).suffix.lower() in BINARY_SUFFIXES:
            continue
        blob = git_bytes("cat-file", "blob", sha)
        if b"\0" in blob[:8000]:
            continue  # binary by content, regardless of extension
        if b"\r\n" in blob:
            failures.append(f"{path} contains CRLF line endings in the index")
    if failures:
        failures.append("fix: git add --renormalize . (see .gitattributes)")
    return failures


def check_doc_refs() -> list[str]:
    """Delegates to docs-loop's own checker. The baseline means this fails on
    NEW broken references only — the repo has a documented, structural
    false-positive class (docs describing OTHER repos) that will never be
    zero, and an always-red check is worse than none."""
    if not CHECK_REFERENCES.exists():
        return [f"missing {CHECK_REFERENCES.relative_to(REPO_ROOT)}"]
    cmd = [sys.executable, str(CHECK_REFERENCES), str(REPO_ROOT), "--strict"]
    if BASELINE.exists():
        cmd += ["--baseline", str(BASELINE)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return []
    new_rows = [l.strip() for l in result.stderr.splitlines() if l.strip().startswith("NEW:")]
    return new_rows or ["check_references.py --strict failed; run it directly for detail"]


def read_frontmatter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    _, _, rest = text.partition("---\n")
    body, _, _ = rest.partition("\n---")
    fields = {}
    for line in body.splitlines():
        key, sep, value = line.partition(":")
        # Only top-level `key: value` lines; a wrapped description continuing
        # onto the next line has no colon and is skipped.
        if sep and not key.startswith((" ", "\t")):
            fields[key.strip()] = value.strip()
    return fields


def check_manifests() -> list[str]:
    failures = []
    for path in sorted(REPO_ROOT.rglob("SKILL.md")):
        rel_dir = path.parent.relative_to(REPO_ROOT).as_posix()
        if rel_dir in VENDORED or ".git" in path.parts or "zip" in path.parts:
            continue
        fm = read_frontmatter(path)
        name = fm.get("name", "")
        version = fm.get("version", "")
        if name != path.parent.name:
            failures.append(f"{rel_dir}/SKILL.md: name '{name}' != directory '{path.parent.name}'")
        if not SEMVER.match(version):
            failures.append(f"{rel_dir}/SKILL.md: version '{version}' is not semver")
        if not (path.parent / "RELEASE_NOTES.md").exists():
            failures.append(f"{rel_dir}: no RELEASE_NOTES.md")
    return failures


def check_packaging() -> list[str]:
    """Build every skill zip as a smoke test, then leave the tree as found.

    The cleanup is not tidiness. `build_skill_zips.py` writes to `zip/`, and
    a `zip/` that exists changes what the doc-refs check sees: a doc quoting
    `zip/something-v1.0.0.zip` resolves as "anchored in a real directory,
    therefore broken" only when the directory is there. Leaving build output
    behind makes doc-refs order-dependent and flaky across re-runs — caught
    by running the two checks in isolation and getting different answers.

    Pre-existing zips are kept: a developer who built them on purpose
    shouldn't lose them to a lint run."""
    script = REPO_ROOT / "scripts/build_skill_zips.py"
    zip_dir = REPO_ROOT / "zip"
    preexisting = zip_dir.exists()
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True
    )
    if not preexisting and zip_dir.exists():
        shutil.rmtree(zip_dir, ignore_errors=True)
    if result.returncode != 0:
        return [f"build_skill_zips.py exited {result.returncode}", result.stderr.strip()[:400]]
    return []


CHECKS = [
    ("exec-bits", check_exec_bits),
    ("line-ends", check_line_endings),
    ("doc-refs", check_doc_refs),
    ("manifests", check_manifests),
    ("packaging", check_packaging),
]


def main(argv: list[str]) -> int:
    only = None
    if "--only" in argv:
        idx = argv.index("--only")
        if idx + 1 >= len(argv):
            print("--only needs a check name", file=sys.stderr)
            return 2
        only = argv[idx + 1]
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0

    selected = [(n, f) for n, f in CHECKS if only is None or n == only]
    if not selected:
        print(f"No such check: {only}. Available: {', '.join(n for n, _ in CHECKS)}", file=sys.stderr)
        return 2

    failed = 0
    for name, fn in selected:
        failures = fn()
        if failures:
            failed += 1
            print(f"FAIL  {name}")
            for line in failures:
                print(f"        {line}")
        else:
            print(f"ok    {name}")

    print()
    if failed:
        print(f"{failed} of {len(selected)} checks failed.")
        return 1
    print(f"All {len(selected)} checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
