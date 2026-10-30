# skill_pack's own conventions

Read this when the skill being drafted or edited will live in `skill_pack`.
It is the detail behind the "Rules that hold for every skill" block at the top
of `SKILL.md`.

When the skill being drafted or edited is going to live in `skill_pack`
(the common case for anyone reaching for this copy instead of the generic
upstream one), layer these on top of the interview above — read
`meta/learn-it/references/skill-authoring-conventions.md` for the full
detail; summarized here:

- Add `metadata:` with `version: "1.0.0"` to the frontmatter (new skill),
  or bump it by hand — semver: patch for wording/doc-only fixes, minor for new
  guidance/steps, major only for an actual contract change — when editing
  an existing one. Every skill in this repo carries this field.
- **`description` has a hard ceiling of 1024 characters** — claude.ai's limit,
  enforced by `scripts/check_repo.py`'s `manifests` check. Write it long and
  information-dense as the guidance above and in
  `meta/learn-it/references/skill-authoring-conventions.md` says, then *check
  the length before committing*. Those two instructions genuinely conflict, and
  the limit wins; following the "be thorough" advice as written naturally
  overshoots. When trimming, cut trigger-phrase examples before cutting the
  statement of what the skill does and how — triggering degrades gracefully
  with fewer example phrasings, and not at all gracefully if the reader can no
  longer tell what the skill is for.
- **Write the description as a YAML block scalar** (`description: >-`, wrapped
  and indented) rather than one long plain line, unless you are certain it
  contains no `": "`. A colon followed by a space inside an unquoted plain
  scalar is invalid YAML — the parser reads it as a nested mapping — and a
  description that quotes a trigger phrase (`Audit mode reviews what exists:
  "..."`) hits this easily. `check_repo.py`'s hand-rolled parser tolerates it,
  so the repo's own checks stay green while every real consumer rejects the
  file. Four skills shipped this way before it was noticed.
- Add a `RELEASE_NOTES.md` next to the new/edited `SKILL.md`:
  reverse-chronological, one dated entry per meaningful change, explaining
  what changed and why.
- Place the skill directory under the right category folder (`my_loops/`,
  `yt_research_for_cc/`, `meta/`) — or flag "this doesn't fit an existing
  category" as its own decision to confirm rather than forcing a fit or
  defaulting silently.
- Keep `SKILL.md` itself lean; push depth into `references/`. Only add
  `scripts/`/`assets/` when there's real content for them.
- After writing or editing, update the root `README.md`'s category table
  and the root `CHANGELOG.md`'s `Unreleased` section, and sanity-check with
  `python3 scripts/build_skill_zips.py` — this repo's own multi-skill
  build, distinct from this skill's own `scripts/package_skill.py` (which
  packages a *single* skill for upload elsewhere). Run both when the skill
  lands in this repo: `package_skill.py` only if the user also wants a
  portable `.skill` file to hand off, `build_skill_zips.py` regardless, as
  the repo-wide sanity check.
- If any new file is a script (`.sh`/`.py` meant to be executed directly),
  verify its executable bit landed as `100755` after `git add` — this repo
  runs `core.fileMode=false`, so a brand-new script needs an explicit check
  (`git ls-files -s <path>`), not an assumption that `chmod +x` alone
  survives staging.
- **The bit does not survive delivery, so don't let a skill depend on it.**
  Whatever it is in git, the sync that hands a skill to a session drops mode
  bits — every script arrives as `0644`, measured at 31 of 31 in a live
  session — so a drafted step that names a script path on its own fails with
  `permission denied`
  ([#1](https://github.com/baileyrd/skill_pack/issues/1)). Any skill drafted
  here that ships scripts must either name the interpreter at each invocation
  (prefix it with `bash` or `python3`) or document the recovery
  (`chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true`).
  `tests/test_script_invocation.py` enforces this and will fail the PR
  otherwise.
- Land the change through this repo's standing PR workflow (branch, PR,
  merge with a merge commit on green CI or no CI) — same as
  `CONTRIBUTING.md` requires for anything else here.

None of this applies when the skill being drafted is explicitly meant for
use *outside* `skill_pack` (e.g. the user wants a `.skill` file to hand to
someone else, unrelated to this repo) — in that case, follow upstream
`skill-creator`'s process unmodified and skip this section entirely.
