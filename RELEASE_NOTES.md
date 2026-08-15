# Release Notes

This repo has no version tags yet, so this file tracks by PR against `main` —
one entry per merged PR, reverse chronological, each linking to its PR.

---

## docs-loop v1.1.0 — cut check_references.py's false positives 26 → 6
**2026-08-15**

- **Added:** component-relative path resolution. Candidates resolve against
  the doc's directory, its nearest enclosing component (a directory with a
  `SKILL.md` or a language manifest), then the repo root. This repo is a
  tree of independently-packaged skills, so shorthand like `scripts/run.sh`
  inside a skill's `references/` was being reported broken on every single
  skill. It now resolves the way a reader reads it. 23 → 18 inline-path
  rows.
- **Fixed:** the checker was parsing markdown link syntax quoted inside
  backticks as a real link, so a release note *documenting* a broken link
  re-reported that link forever. Found because this repo's own release notes
  did exactly that — the entry describing the `#operators-in-expressions`
  fix was itself reported as a broken anchor, twice. Code spans are now
  masked before link extraction; path candidates still come from the code
  spans. 3 broken anchors → 0.
- **Added:** `historical-*` verdicts for non-resolving paths in
  `CHANGELOG`/`RELEASE_NOTES` files. A path in a past entry that no longer
  exists is usually the log doing its job, and docs-loop's own Rules already
  say never to rewrite a past entry — so reporting those as `broken` was
  sending an auditor at rows they're forbidden to act on. 55 rows moved off
  the action list without disappearing from the report.
- **Verified no real finding was lost:** the two genuine findings from the
  v1.0.0 run were already fixed in the previous change, and the remaining 6
  `broken` rows were each read individually. All 6 are the structural class
  the skill's Limitations already names — a doc describing a *different*
  component or repo — or build-state-dependent (`README.md`'s `zip/`
  example, which resolves or not depending on whether zips were built).
- **Not chased:** the ~150 `unresolved` rows. That verdict exists precisely
  to hold "might be a runtime file, an example, or prose with a slash in
  it," and driving it to zero would mean tightening heuristics until real
  findings vanish with the noise.

## Work docs-loop's first two findings (#16, #17)
**2026-08-15** · [#16](https://github.com/baileyrd/skill_pack/issues/16) · [#17](https://github.com/baileyrd/skill_pack/issues/17)

- **Fixed:** `my_loops/dedupe-loop` (v1.1.1) —
  `references/platform-directory.md` told the reader
  `scripts/scan_platform_repos.sh` would clone a repo that wasn't checked
  out. That script exists in four sibling skills and not in this one. What
  the reading turned up is bigger than the wrong filename: dedupe-loop has
  no clone path at all, and `index_capabilities.sh` takes a local directory,
  so an un-checked-out `PLATFORM_REPOS` entry silently can't be indexed. The
  section now documents the actual workflow (`gh repo clone ... --depth 1`,
  namespace caveat intact), step 1 states the local-path requirement instead
  of leaving it to a usage error, and Limitations records the absent clone
  path as a deliberate choice — porting the sibling's script would add a
  `gh` dependency this skill otherwise doesn't need.
- **Fixed:** `web_dev/datastar-pro` (v1.0.1) — `references/core.md`'s TOC
  entry `[Operators in Expressions](#operators-in-expressions)` pointed at
  nothing; the heading is `### Operators` (slug `#operators`), and the entry
  was listed after `Action Calls` when its section precedes it. Fixed the
  TOC rather than the heading: the heading is the content, the TOC is a
  pointer at it.
- **Not fixed, deliberately:** the other 16 `broken` rows from the same
  checker run. They're the documented cross-repo false-positive class —
  docs here describing *other* repos, skill-relative shorthand, and
  `CHANGELOG.md`'s pointer to a file it correctly records as removed. Two
  real findings out of 18 candidates is the ratio the skill's own
  Limitations predicts, and acting on the other 16 would have meant
  vandalising accurate docs.
- **Follow-up worth doing, not done here:** `check_references.py` resolves
  a candidate path against the doc's own directory and the repo root only.
  Most of this repo's shorthand (`scripts/audit.sh` inside a
  `references/` subdirectory) would resolve if it also tried the nearest
  ancestor containing a `SKILL.md`. That would cut the false-positive class
  substantially — a change to the tool, kept out of a change that was
  supposed to be about the two findings.

## Add my_loops/docs-loop — documentation review/update loop
**2026-08-15** · branch `claude/docs-review-loop-skill-ih5zhr`

- **Added:** `my_loops/docs-loop` (v1.0.0) — reviews a target repo's
  documentation against the current state of its code and updates it. Order
  is the whole point: ground truth from manifests/entry points/`--help`/CI/
  the real tree *first*, prose second, because reading the docs first turns
  an audit into a proofread. Findings are classified six ways (`stale` /
  `missing` / `orphaned` / `aspirational` / `unverifiable` / `accurate`) in a
  `docs-audit.md` checkpoint before any edit; `accurate` and `unverifiable`
  rows persist across runs so a re-audit doesn't re-litigate settled claims.
- **Added:** `scripts/inventory_docs.sh` (per-doc drift ranking: last
  changed, plus commits to non-doc files since) and
  `scripts/check_references.py` (relative links, GitHub heading anchors,
  backticked repo paths, shell-block paths — stdlib only). The checker
  separates `broken` (path anchored in a directory that really exists, so
  the claim is about this tree and is false) from `unresolved` (could be a
  runtime file, an example, or prose with a slash in it) — conflating them
  buried 11 real findings under ~300 rows of noise in the first pass here.
- **Found while testing, not fixed here:** the checker reports 18 `broken`
  rows against `skill_pack`. Reading each one — which is exactly the step
  the skill insists on, since the script surfaces candidates and never
  renders a verdict — **two** are real drift:
  `my_loops/dedupe-loop/references/platform-directory.md:60` names
  `scripts/scan_platform_repos.sh`, which its three sibling copies do have
  and dedupe-loop does not (its scripts are `index_capabilities.sh` /
  `find_clusters.py`); and
  `web_dev/datastar-pro/references/core.md:11`'s TOC links
  `#operators-in-expressions` against a heading that slugs to `operators`.
  Both left for a real docs-loop run to take through its own checkpoint
  rather than hand-patched inside the change that added the tool.
- **The other 16 are the documented false-positive class**, and the ratio is
  the point: most docs here describe *other* repos or use skill-relative
  shorthand (`scripts/audit.sh` meaning repo-config's), and `CHANGELOG.md`'s
  pointer to the removed `need_to_productize/datastar-pro.skill` is correct
  history, which this skill's own rules say never to "fix." Documented in
  the skill's Limitations and the script's docstring rather than filtered
  out by a heuristic that would have hidden the two real findings with them.
  One row is also build-state-dependent (`README.md`'s
  `zip/dedupe-loop-v1.0.0.zip` resolves or not depending on whether
  gitignored `zip/` output is present) — run against a clean tree.

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
