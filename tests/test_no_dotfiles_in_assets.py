#!/usr/bin/env python3
"""Guard: no skill may ship a dot-prefixed path under assets/.

The bug this would have caught (issue #41): the sync that delivers a skill to
a session copies with a glob that doesn't match dotfiles, so every dot-prefixed
entry under `my_loops/repo-config/assets/templates/` was silently absent from
the delivered copy — `.gitattributes`, `.github/ISSUE_TEMPLATE/`,
`.github/PULL_REQUEST_TEMPLATE/`, and both CI workflows. `apply.sh` could not
write files that weren't there, so a target repo could not reach 11/11 through
the skill as synced, and the operator had to notice and hand-write them.

The sync itself lives outside this repo and can't be fixed from here. What can
be fixed from here is not depending on it: templates are stored under a `dot-`
prefix and `apply.sh` restores the real name on write. This test is what keeps
that convention from being quietly undone by someone "tidying up" the names.

It is deliberately repo-wide rather than scoped to repo-config. repo-config is
the only skill shipping dotfiles today; the point is that the next one to try
fails here instead of in a target repo six months from now.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Skill roots are `<category>/<skill>/`; a skill's payload lives in assets/.
ASSET_DIRS = sorted(REPO_ROOT.glob("*/*/assets"))


class TestNoDotfilesInAssets(unittest.TestCase):
    def test_asset_dirs_exist(self):
        """Guard the guard: a glob that silently matches nothing would make
        every assertion below vacuously true."""
        self.assertTrue(
            ASSET_DIRS,
            "found no */*/assets directories — the glob is wrong, not the repo",
        )

    def test_no_dot_prefixed_paths_under_assets(self):
        offenders = []
        for assets in ASSET_DIRS:
            for path in assets.rglob("*"):
                rel = path.relative_to(REPO_ROOT)
                # Check every segment below assets/, not just the basename:
                # `.github/workflows/ci-rust.yml` has an undotted basename and
                # is dropped by the sync all the same.
                depth = len(assets.relative_to(REPO_ROOT).parts)
                for seg in rel.parts[depth:]:
                    if seg.startswith("."):
                        offenders.append(str(rel))
                        break

        self.assertEqual(
            [], sorted(offenders),
            "dot-prefixed paths under assets/ are dropped by the skill sync "
            "(issue #41). Store them with a `dot-` prefix and have the skill's "
            "apply script restore the real name on write:\n  "
            + "\n  ".join(sorted(offenders)),
        )


if __name__ == "__main__":
    unittest.main()
