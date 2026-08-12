# Release Notes

This repo has no version tags yet, so this file tracks by PR against `main` —
one entry per merged PR, reverse chronological, each linking to its PR.

---

## PR #4 — Fix silent exec-bit loss in build_skill_zips.py
**2026-08-12** · [#4](https://github.com/baileyrd/skill_pack/pull/4)

- **Fixed:** `scripts/build_skill_zips.py` shipped scripts non-executable
  (`0o644`) in the built zip whenever a `scripts/*.sh`/`*.py` file was
  genuinely edited and its `+x` bit didn't survive `git add` — the only
  safety net, `restore_exec_bits.py`, restores `+x` by matching a file's
  *content* against a blob that was `100755` at `HEAD`, so it only
  catches unmodified moves/copies, not real edits. Reproduced against a
  scratch clone: edited `apply.sh`, staged it at `644`,
  `restore_exec_bits.py` correctly no-op'd (content genuinely changed),
  and the built zip shipped `apply.sh` at `0o644` with no warning.
- **Fixed by:** `git_file_mode()` now checks the file's shebang (`#!`)
  first — a signal independent of git's index or the OS-reported mode
  entirely — and only falls back to the git-index check for the rare
  executable with no shebang. Verified the fix against the same
  reproduction: same edit, same staged `644`, zip now ships `0o755`.
  Rebuilt all 8 skills' zips and confirmed every `.sh`/`.py` file across
  all of them lands at `0o755`.
- **Traced to:** the `rusty_dbs` sync-gap finding logged in
  `my_loops/repo-config/RELEASE_NOTES.md` ("Third occurrence of the same
  sync-gap pattern") — this fixes the exec-bit half of that finding at
  the source (the build script), not just the symptom. The `.github/`-
  missing half is unaffected by this change; `Path.rglob("*")` was
  checked directly and does traverse dot-prefixed directories correctly
  in this repo's Python, so that symptom still points at something
  upstream of the build (a stale/incomplete local clone at build time),
  not at `build_skill_zips.py`.

## PR #2 — Apply repo-config's standard governance file set to skill_pack itself
**2026-08-12** · [#2](https://github.com/baileyrd/skill_pack/pull/2)

- **Added:** `.github/PULL_REQUEST_TEMPLATE/` (feature, bug_fix, docs, chore),
  `.github/ISSUE_TEMPLATE/` (bug_report, feature_request, config.yml),
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`,
  `ARCHITECTURE.md`, and a `docs/adr/0001-template.md` seed — the standard
  set the repo's own `my_loops/repo-config` skill applies to other repos,
  run here against `skill_pack` for the first time.
- **Changed:** `README.md` gained Architecture/Contributing/Security/License
  sections linking to the new files; existing prose left untouched.
- `ARCHITECTURE.md`'s boundary table and non-goals were filled in for real
  rather than left as scaffold — this repo has no service/process boundary
  between skills (each is independently consumed by an external harness), so
  the generic ports-and-adapters default doesn't apply as written. Per
  `ATLAS-100`'s own trigger clause and `ATLAS-PHIL-0102` (Justified
  Complexity) in `baileyrd/Atlas_Engineering_Standards_Library`, the real
  boundary documented instead is the `SKILL.md` manifest contract between a
  skill directory and the harnesses that load it.
- **No CI workflow added:** neither `Cargo.toml` nor `pyproject.toml`/
  `setup.py` exists at repo root (the `.py` scripts under `scripts/` have no
  package manifest), so `apply.sh`'s stack-selected CI step had nothing to
  select — consistent with the skill's "no manifest, no workflow" rule
  rather than a gap.
- `SECURITY_CONTACT` resolved to the repo owner's email from the existing
  `git remote` (`baileyrd/skill_pack`), not a placeholder — this repo was
  non-greenfield going in (README and git history already existed).
- This root-level file is separate from the per-skill `RELEASE_NOTES.md`
  files each skill under `my_loops/`/`yt_research_for_cc/` already keeps
  (e.g. `my_loops/repo-config/RELEASE_NOTES.md`) — those track that skill's
  own authoring history; this one tracks changes to `skill_pack` as a repo.
