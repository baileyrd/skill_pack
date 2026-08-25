# Release Notes

issue-loop lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/issue-loop),
where changes land through a PR per `CONTRIBUTING.md` — this log tracks
merged PRs, the same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.9.0 — Name the obvious gh substitutes too, gate the triage table for real, require a standards-check acknowledgment
**2026-08-25**

Applied from the step-5 wrap-up retro on the `issue-loop` run against
`baileyrd/rusty_gui` ([#5](https://github.com/baileyrd/rusty_gui/pull/5),
[#6](https://github.com/baileyrd/rusty_gui/pull/6),
[#7](https://github.com/baileyrd/rusty_gui/pull/7)), which closed rusty_gui#2
and #4 (a Windows event-pump feature and a from-scratch Linux/X11 backend)
and left #3 (macOS) deferred with a `needs-human` label. Six findings were
reported; one (the reuse-search substitute) turned out to already be fixed by
v1.7.0, discovered only by re-reading this file fresh before applying
anything — same as the v1.8.0 entry below found for its own F1/F3. One
(the cosmetic finding on step 3.3's needs-new-dependency ask needing two
rounds when multiple issues land in the bucket at once) was explicitly
declined by the user as not worth an edit. The four below are what's left.

- **Added (missing-guardrail, `costly-guess`):** step 0's gh-absent
  substitute list named issue-list, reuse-search, and CI-wait-and-merge, but
  not PR creation (step 3.8), closure re-confirmation (step 3.10), or
  `needs-human` labeling/commenting (step 1) — this run had to infer
  `create_pull_request`/`issue_write`/`add_issue_comment` as the right tools
  on its own. Now named, flagged explicitly as less subtle than the other
  two substitutes (nothing session-scoped or timing-dependent blocks them).
- **Added (missing-guardrail, `could-have-caused-real-damage`):** the
  repo-config prerequisite already bounds a *pre-existing-code* CI failure
  (v1.8.0, below) but said nothing about a target that ships
  platform-conditional code. `rusty_gui`'s CI was single-OS (`ubuntu-latest`)
  while the crate had real `#[cfg(windows)]` code — a Windows-only feature
  could have merged with **zero CI coverage of its own logic**, silently,
  since the runner never even compiles code gated to a different OS. Now:
  check whether the workflow's OS matrix actually matches what the crate
  ships.
- **Added (missing-guardrail, `costly-guess`):** step 1's "report the triage
  table" line was true but easy to silently skip in a busy autonomous run —
  this run classified all three issues correctly but never posted the table
  as its own message before starting step 2/3; the first user-facing
  artifact was already a stop-and-ask about one of the flagged issues.
  Reworded as an explicit hard gate rather than a narrative aside.
- **Added (missing-guardrail, `costly-guess`):** step 3.5's
  development-standards check ("check `references/development-standards.md`
  ... before falling back to this repo's own conventions") had no
  requirement to say which happened. This run fell back to the target
  repo's own conventions for both issues with no record the standards repos
  were ever actually checked. Now requires a one-line acknowledgment per
  issue — a cited requirement, or an explicit "neither applied."

---

## v1.8.0 — Bound the CI-baseline-fix, and keep every log current
**2026-08-25**

Applied from the step-5 wrap-up retro on the `issue-loop` run against
`baileyrd/rusty_gpu` ([rusty_gpu#4](https://github.com/baileyrd/rusty_gpu/pull/4)),
which closed rusty_gpu#2. Six findings were reported; three (F1's reuse-search
substitute, F3's harness branch exception) turned out to already be fixed by
v1.7.0's own retro-driven changes, discovered only by re-reading this file
fresh before applying anything — the two below are the ones still open.
F4 and F6 (verifying a cross-repo blocking claim in triage; no keyword-search
mechanism for the development-standards check) were reported and **not**
applied — real but single-run, logged here per `skill-retro`'s Limitations
rather than acted on immediately.

- **Added (F2, `costly-guess`/`could-have-caused-real-damage`):** the
  repo-config prerequisite now bounds what "establish a green CI baseline"
  covers. On the run that prompted this, `repo-config`'s new `ci-rust.yml`
  immediately failed against rusty_gpu's *pre-existing* code (unformatted
  source, one unused-variable lint) — unrelated to the issue actually being
  worked. Both were trivial, so fixing them inline in the same prerequisite
  commit was a reasonable call, but nothing said so: a repo whose pre-existing
  failures were substantial instead of two lines could have pulled a
  same-commit "baseline fix" into real, unreviewed scope creep bundled onto an
  unrelated PR. Now: trivial/mechanical fixes stay inline, anything larger
  gets filed as its own issue.
- **Added (F5, `costly-guess`):** step 3.7 and the matching Rules bullet
  named only `RELEASE_NOTES.md`, even though `repo-config` — this skill's own
  stated prerequisite — seeds both `RELEASE_NOTES.md` and `CHANGELOG.md`, and
  `repo-config`'s own text calls updating only one of them "the common
  failure, not rare." This run updated both by generalizing from
  `repo-config`'s convention; a run treating this file as self-sufficient
  (which is the point of it being self-contained) would plausibly have missed
  `CHANGELOG.md`. Both now say to keep every log the repo has current, not
  just one.

---

## v1.7.0 — The gh-less path, spelled out end to end
**2026-08-19**

Applied from the step-5 wrap-up retro on the `issue-loop` run against
`rusty_naner` that shipped its `naner suggest` command
([rusty_naner#108](https://github.com/baileyrd/rusty_naner/pull/108)) — a
Claude Code web session with no `gh` binary at all, which exercised every
substitution path at once. All five findings applied as one approved batch.

- **Added:** step 0's preflight now names the *working* substitute per
  script, not just "use the MCP tools." The reuse search can't go through
  the MCP search tools at all — session repo scoping blocks unattached
  repos, which the platform repos always are — so the documented path is
  attach-read-only, shallow-clone, `rg`. CI-wait-and-merge gets its actual
  wait mechanism written down: `subscribe_pr_activity` plus a `send_later`
  check-in, check runs matched by `head_sha`, merge commit via the MCP
  merge tool. On the run that prompted this, both were rediscovered from
  scratch mid-loop.
- **Added:** the repo-config prerequisite acknowledges its own `audit.sh`
  is `gh`-dependent — the same preflight that just found `gh` absent was
  being told to run a script that needs it. A direct governance-file
  inspection of the checkout now explicitly satisfies the check.
- **Added:** step 3.4's branch-naming rule gets a harness exception: a
  session that arrives with a designated `claude/...` branch and a
  never-push-elsewhere rule uses that branch for the PR. The run had to
  choose between violating the skill and violating the harness; now the
  precedence is written down.
- **Added:** interactive harness mode with nobody actually reachable (the
  common case for web/remote runs, where `LOOP_HARNESS_MODE` is simply
  unset) now explicitly degrades to auto mode's label-and-move-on for
  ambiguity, instead of implying a question that would block forever.

---

## v1.6.1 — Fix this log's own stale "no PR workflow yet" header
**2026-08-17**

- **Fixed:** this file's own preamble still said "pushed direct to `main`
  (no PR workflow yet)." `CONTRIBUTING.md` and the merge history for v1.6.0
  itself (PR [#79](https://github.com/baileyrd/skill_pack/pull/79)) show
  that's no longer true — changes here land through a PR like everywhere
  else in this repo. Reworded to say so.
- **Why:** flagged as a follow-up in the v1.6.0 entry's own PR description
  rather than fixed inline there, to keep that PR's diff scoped to the
  `skill-retro` findings it was actually about.
- **Scope note:** `repo-config`'s own `RELEASE_NOTES.md` carries the
  identical stale claim and wasn't touched here — out of scope for this
  skill's own log.

---

## v1.6.0 — Infer TARGET_REPO when obvious, scope free-text args, don't bootstrap before triage
**2026-08-17**

- **Added:** `TARGET_REPO` may be inferred when exactly one repo is attached
  to the session, instead of always halting when it isn't spelled out
  explicitly. The halt rule in step 0's last bullet is unchanged for real
  ambiguity (multiple repos, none named).
- **Added:** explicit scope for free-text arguments beyond `TARGET_REPO` —
  they filter which *already-open* issues get worked, never license to
  invent issues from a doc's prose or a file's TODOs. A filter matching
  zero issues gets reported as such, not reinterpreted more expansively.
- **Changed:** the repo-config prerequisite no longer bootstraps
  unconditionally whenever the governance score is low. The `audit.sh`
  check still always runs (cheap), but the actual `repo-config` invocation
  now waits for step 1's triage to confirm at least one actionable issue
  exists first — bootstrapping a repo's full governance-file set ahead of
  a triage pass that turns up nothing was pure waste.
- **Why:** found by a `skill-retro` pass grounded in a real run against
  `baileyrd/rusty_prime_agent` — args were "against &lt;two doc filenames&gt;"
  with no repo named (only one repo attached to that session), triage found
  zero open issues, and the repo-config prerequisite would otherwise have
  bootstrapped a full governance-file set for a repo with nothing to
  actually work.
- **Scope note:** that same retro pass also flagged the gap `gh`-unavailable
  environments have no fallback — already closed independently by v1.3.0's
  tooling preflight, before this run's synced copy of the skill (v1.1.1)
  had caught up to it. No action needed here; recorded so the retro's
  finding doesn't look silently dropped.

---

## v1.5.0 — Don't depend on an executable bit the sync drops
**2026-08-17**

- **Added:** a first item in step 0's tooling preflight documenting how to restore the executable bit —
  `chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true`, with naming the
  interpreter (`bash scripts/x.sh`) as the fallback where the skill directory
  is read-only.
- **Why ([#1](https://github.com/baileyrd/skill_pack/issues/1)):** the sync
  that delivers a skill to a session doesn't preserve mode bits. Measured in a
  live session: **31 of 31 shebanged scripts across all ten skills arrive as
  `0644`**, so any step written `scripts/x.sh` fails with `permission denied`.
  The issue had recorded this as an occasional symptom; it is universal.
- **Scope note:** this documents a recovery rather than fixing the sync, which
  lives outside this repo. #1 stays open.

---

## v1.4.0 — One `Closes` keyword per issue, and verify it fired
**2026-08-16**

From this skill's own wrap-up retro, grounded in the run that cleared
`skill_pack`'s backlog — 15 issues across 7 PRs.

- **Fixed (finding J1):** step 8 said `Closes #<N>`, singular. Batching issues
  by target skill made multi-issue PRs the norm, and the natural-looking
  `Closes #52, #53, #54, #55` closes **only #52** — GitHub honours the keyword
  only where it *immediately precedes* a number. **Eight issues stayed open
  after their fixes merged** (#42, #43, #46, #47, #48, #53, #54, #55) and were
  only caught by re-listing the backlog at wrap-up. Step 8 now requires one
  `Closes` per issue and says why the comma form fails.
- **Changed:** step 10 was "confirm the issue actually closed" — easy to read as
  a formality. It now requires re-listing open issues rather than assuming the
  keyword fired, names the failure as silent (the merge succeeds, the PR looks
  finished), and says to close stragglers by hand before continuing, so the next
  loop-around isn't triaging work that is already done.

**Severity note:** this is `costly-guess`, not `cosmetic`. Nothing broke, but
the backlog was left in a state that misrepresented what had been done — and the
next run of this loop would have re-triaged and potentially re-worked eight
already-fixed issues.

Two sibling findings from the same retro were reported and **not** applied:
anticipating shared-file conflicts across sequential batch PRs, and giving the
skill vocabulary for the batching deviation itself. Both are real but
single-run; logged here rather than acted on, per `skill-retro`'s Limitations.

---

## v1.3.0 — Preflight the loop's own tooling
**2026-08-16**

From a `skill-retro` pass on this skill, grounded in a run against
`baileyrd/skill_pack` that **halted at step 1**. All three findings share a
theme: the skill validated the *target repo* before starting and never
validated its own execution environment.

- **Added ([#61](https://github.com/baileyrd/skill_pack/issues/61)):** step 0
  gains a tooling preflight — `command -v gh`, one cheap API read, and a note
  on which CI-status mechanism the target uses. The run that prompted this
  found `gh` **not installed at all** (Claude Code on the web), which makes all
  three scripts unrunnable including `watch_and_merge.sh`, load-bearing for
  step 3 rather than a convenience. The MCP substitution had to be improvised
  mid-run; it's now named.
- **Added:** an infrastructure **stop condition**. Every existing one was about
  work state (no issues left, red CI, breaking change); none covered the
  tooling going away, which is the case where partial state exists and matters.
  It requires reporting completed / in-flight / never-started separately, and
  explicitly forbids falling back to title-only triage to keep going — step 1
  already says titles aren't sufficient, and a rate limit isn't a reason to
  lower that bar.
- **Changed:** Limitations now distinguishes `gh` *absent* from `gh`
  *unauthenticated* — the second fails loudly on first use, the first silently
  removes every script. The Scripts table says outright that all three need
  `gh`.
- **Note:** the sibling loops (`parity-loop`, `sovereignty-loop`,
  `dedupe-loop`, `rust-migration`) share the same `gh`-shaped scripts and the
  same Limitations wording, so they likely have the same gap. Not verified
  here — only `issue-loop` actually ran — and left on #61 as a set to check
  rather than patched blind.

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

## v1.1.1 — Declare jq and ripgrep
**2026-08-15**

- **Fixed:** the Scripts note said "shell out to `gh`/`git` only — no extra
  dependencies." Both false. `next_issue.sh:27` pipes through **`jq`**
  (required), and `scan_platform_repos.sh:51` uses **`ripgrep`** when
  present, falling back to `grep` — so optional, and now documented as such
  rather than as an absence.
- Found by `docs-loop` row 5.

## v1.1.0 — Wire skill-retro into wrap-up (step 5)
**2026-08-13**

- **Added:** step 5, "Wrap-up retro" — after step 4's report, runs a
  `meta/skill-retro` pass on `issue-loop` itself, grounded in this run's
  step 1 triage and step 2 reuse-check calls. Read-only, safe unattended in
  either harness mode; applying anything found is a separate,
  explicitly-approved follow-up.
- Part of a batch wiring the same convention into every remaining
  `my_loops` skill, following the pattern first used on
  `my_loops/rust-migration` v1.1.0 and `meta/skill-retro`'s own step 6.

## v1.0.0 — Initial versioned release
**2026-08-12**

- **Added:** `version: 1.0.0` to `SKILL.md` frontmatter and this file — first
  formally versioned cut of the skill. No behavior change; establishes the
  baseline the next entry will diff against.
