# Release Notes

dedupe-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/dedupe-loop),
pushed direct to `main` (no PR workflow yet) — this log tracks commits instead of
PRs, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.3.0 — Tooling preflight and an infrastructure stop condition
**2026-08-16**

- **Added:** a **tooling preflight** as the first bullet of step 0 — `command
  -v gh`, one cheap API read, and a note on which CI-status mechanism the
  target uses. The bullets it sits above all validate the *target*; this one
  validates the loop's own execution environment, which is what actually fails
  first when it fails.
- **Added:** an **infrastructure stop condition** — an unreachable or
  rate-limited GitHub API halts cleanly and reports three lists (completed, in
  flight with branch and PR named, never started) plus the retry path. Every
  other stop condition in this skill is about work state; this is the one where
  partial state exists and something can be stranded unnamed.
- **Added:** the preflight names the two CI-status traps by their symptom:
  a repo reporting via Actions checks returns `total_count: 0` from the
  commit-status endpoint (not evidence CI is missing), and runs associate to
  PRs by *branch*, so a stale run from an earlier PR on a reused branch can
  read as a pass for code it never ran against. Match by `head_sha`.
- **Documented:** which scripts require `gh`, in both the Scripts section and
  Limitations. `next_issue.sh` and `watch_and_merge.sh` do; `find_clusters.py`
  and `index_capabilities.sh` don't and keep working without it. Limitations
  previously said nothing about `gh` at all.
- **Fixed:** the no-clone-path limitation claimed porting
  `scan_platform_repos.sh` here "would add a `gh` dependency this skill
  otherwise doesn't need" — but `next_issue.sh` and `watch_and_merge.sh`
  already need it. Narrowed to the claim that's true: it would add one to
  *step 1*, which otherwise runs entirely off local checkouts.

**Evidence, stated honestly:** only `issue-loop` actually failed this way in a
live run — `gh` absent in a web session, so its scripts couldn't run and the
loop had to be re-derived mid-flight. The gap here was confirmed structurally
by reading this skill, not by a failing run of it. The change is documentation
only — no behavior changes and no scripts touched — so the cost of being wrong
is low, but it isn't the same grade of evidence
([#61](https://github.com/baileyrd/skill_pack/issues/61)).

---

## v1.2.0 — Refresh the stale platform repo directory
**2026-08-15**

- **Fixed:** `references/platform-directory.md` was wrong in a way that broke
  the scan step, not just incomplete. It listed ~25 repos under `Rusty-Mill/*`
  — rustils, rusty_json, rusty_http, rusty_libc, rusty_tokio, rusty_wire and
  others — when all of them live under `baileyrd`. Only four repos are actually
  in the Rusty-Mill org. Since the file's own "Resolving a bare repo name"
  section tells the scan script to build clone URLs from that column, every one
  of those lookups would 404.
- **Fixed:** it listed 30 repos against an actual 80+, missing `rusty_sync`,
  `rusty_wire`, `rusty_codec`, `rusty_stream` and others. Two of those turned
  out to be the relevant candidates in a real audit.
- **Fixed:** three entries don't exist under the names given — `rush`,
  `rusty_compactor` (it's `rusty_token_compactor`), `rusty_tail` (it's
  `rusty_tailscale`). `rusty_async` exists but is an empty repository.
- **Changed:** regrouped by function; purposes not confirmed by reading source
  are now marked `†` rather than asserted; added a note that `platform`'s
  `thiserror` dependency pulls syn/quote/proc-macro2/unicode-ident into every
  consumer of the platform layer.

## v1.1.2 — Correct the dependency line
**2026-08-15**

- **Fixed:** the Scripts note claimed everything "shells out to
  `gh`/`git`/`ripgrep` only." Two errors in one sentence: no script here
  invokes `ripgrep` at all (that claim was inherited from a sibling), and
  `next_issue.sh:33` pipes `gh` output through **`jq`**, a hard requirement
  the "no extra dependencies" wording denied. The script's own header
  declared `jq` correctly the whole time; only the SKILL.md was wrong.
- Found by `docs-loop` row 5, which started as a single undeclared PyYAML
  import in `meta/my-skill-creator` and turned out to span six skills.

## v1.1.1 — Stop documenting a clone script this skill doesn't have
**2026-08-15**

- **Fixed:** `references/platform-directory.md`'s "Resolving a bare repo
  name" section told the reader that `scripts/scan_platform_repos.sh` would
  clone a repo not checked out locally. This skill has no such script — its
  four are `index_capabilities.sh`, `find_clusters.py`, `next_issue.sh`,
  `watch_and_merge.sh` — and nothing in it clones anything. The paragraph
  came along when the reference file was copied from a sibling that *does*
  ship that script; the script didn't come with it.
- **Fixed by:** rewriting the section for how this skill actually works —
  `index_capabilities.sh` takes a local path, so an un-checked-out repo
  needs a `gh repo clone ... --depth 1` first, and the Namespace column is
  what builds that slug. Shallow is enough; the indexer reads the working
  tree and never touches history.
- **Changed:** step 1 now says the argument is a local path rather than
  leaving it to the script's usage error, and Limitations records the
  missing clone path as a deliberate choice — porting the sibling's
  `scan_platform_repos.sh` would add a `gh` dependency this skill otherwise
  doesn't need, so it stays a separate decision rather than an assumed gap.
- **Found by:** `my_loops/docs-loop`'s first run against this repo
  ([#16](https://github.com/baileyrd/skill_pack/issues/16)) — surfaced by
  `check_references.py` as an unresolvable path, confirmed by reading, which
  is what turned "wrong filename" into "no clone path at all."

## v1.1.0 — Wire skill-retro into wrap-up (step 5)
**2026-08-13**

- **Added:** step 5, "Wrap-up retro" — after step 4 ends (clusters fully
  adopted, some deferred, or stopped mid-way), runs a `meta/skill-retro`
  pass on `dedupe-loop` itself, grounded in this run's step 2 clustering/
  classification and step 4.1 behavioral calls. Read-only, safe unattended
  in either harness mode; applying anything found is a separate,
  explicitly-approved follow-up.
- Part of a batch wiring the same convention into every remaining
  `my_loops` skill, following the pattern first used on
  `my_loops/rust-migration` v1.1.0 and `meta/skill-retro`'s own step 6.

## v1.0.0 — Initial versioned release
**2026-08-12**

- **Added:** `version: 1.0.0` to `SKILL.md` frontmatter and this file — first
  formally versioned cut of the skill. No behavior change; establishes the
  baseline the next entry will diff against.
