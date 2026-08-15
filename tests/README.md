# tests

```bash
python3 -m unittest discover -s tests -v
```

Stdlib `unittest`, no third-party dependency — deliberately. PyYAML is
already the only third-party module imported anywhere in this repo
(`meta/my-skill-creator/scripts/quick_validate.py`), and it's documented as
an exception rather than a precedent. A test runner that needs installing
would make the suite something you can only run after setup, which is how
suites stop being run.

## What's tested, and why these things

The same admission rule ADR-0002 sets for repo checks applies here: **a test
earns its place by naming the bug it would have caught.** Nearly every test
below reproduces a defect that actually shipped or was caught mid-review in
this repo — most of them in `check_references.py`, whose logic is subtle
enough to have been wrong four separate times in one day.

Not aiming for coverage. Aiming for the specific mistakes this code has
already proven it makes.

| Test module | Covers |
| --- | --- |
| `test_check_references.py` | `docs-loop`'s reference checker: slug generation, code-span masking, path classification, component roots, historical downgrade, baseline keys |
| `test_check_repo.py` | Frontmatter parsing used by the `manifests` check |

## What isn't tested, and why

The checks that shell out to `git` (`exec-bits`, `line-ends`) and the
packaging smoke test aren't unit-tested here. They're verified by fault
injection instead — documented in ADR-0002 — because their behavior *is* the
integration with git and the filesystem, and a mock of `git cat-file` would
test the mock. Reproducing the real fault is the stronger check, and it's
what caught the two cases where a check silently passed when it shouldn't
have.
