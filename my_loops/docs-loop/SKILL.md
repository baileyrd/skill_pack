---
name: docs-loop
description: Reviews a repo's documentation against what the code actually does right now, then updates it — builds ground truth from the manifest, entry points, CLI help, scripts, CI workflows, and the real directory tree FIRST, then audits every checkable claim in README/ARCHITECTURE/CONTRIBUTING/docs/ADRs and public doc-comments, classifying each as accurate, stale, missing, orphaned, aspirational, or unverifiable in a `docs-audit.md` checkpoint before a single edit lands. Use whenever the user asks for a documentation review, wants docs updated to match the current state of the repo, wants drift/rot checked after a batch of merged work, wants README or ARCHITECTURE brought up to date, wants broken doc links and dead file paths found, asks "are the docs still right", or names it (docs-loop, doc review loop, docs drift loop). Companion to repo-config, which installs the governance file SET and only checks those files are PRESENT — this one checks whether their CONTENT is still true; same PR/CI/merge mechanics as its my_loops siblings. Checkpointed with per-finding sign-off by default, proceeding unattended on verifiable stale-fact and broken-reference rows when `LOOP_HARNESS_MODE=auto` (any finding where the CODE looks wrong rather than the doc always still waits).
version: 1.2.1
---

# docs-loop

Turns "the docs have drifted" into a bounded loop: build ground truth from the
code → inventory the doc surface → audit every claim against that ground truth
→ get sign-off → fix, per doc, through PRs → verify → repeat until the audit
comes back clean.

The failure mode this exists to close is *confirmation reading*: opening
README.md, finding it plausible, and calling the docs reviewed. Documentation
rot is asymmetric — a stale claim reads exactly like an accurate one, and only
a check against the actual tree tells them apart. So the order below is not
negotiable: **ground truth first, docs second.** Reading the docs first anchors
you, and you will confirm rather than check.

This skill edits documentation only. Where the docs are right and the *code* is
wrong, that's a finding to hand back, never something to quietly paper over in
either direction (see Rules).

`assets/templates/` is the payload copied into the TARGET repo (an issue body
template). This skill's own files describe the loop itself — don't confuse the
two.

## Run (when invoked)

**0. Scope**
- `TARGET_REPO` — whose docs are being reviewed. Defaults to the current
  repo. This repo (`skill_pack`) is a legitimate target for it too: its
  root `README.md` category tables and `ARCHITECTURE.md` "Structure"
  section both drift every time a skill is added or moved.
- **repo-config relationship**: `repo-config`'s `scripts/audit.sh
  <TARGET_REPO>` answers *which standard docs exist*; that script says so
  itself ("checks file *presence*, not *currency*"). Run it if the target's
  governance set has never been applied — a missing README is repo-config's
  job to create, not this loop's to review. Everything past presence is
  this skill's job. Don't re-run it if a prior step this session already
  covered it.
- **Doc surface** — default scope is every tracked `*.md`/`*.mdx` in the
  repo, plus doc-comments on the public API surface (`///` / `//!`,
  docstrings, JSDoc). Generated API reference output (rustdoc HTML, Sphinx
  builds) is out of scope — review the source comments it's generated from,
  not the artifact.
- **Review depth** — default is the full current state, not a diff since
  some marker. If the user scopes it to "since the last release" or "the
  docs touched by these 6 merged PRs", honor that, and say in the report
  that the audit was scoped rather than whole-repo.

**1. Ground truth** — build it from the repo, before opening any prose doc.
`references/ground-truth-sources.md` lists, per stack, exactly which
artifacts are authoritative for what: manifests (name, version,
dependencies, features, entry points), `--help` output, the `scripts/` and
`.github/workflows/` trees, the public API surface, the real directory
layout, and the ADR log. Two rules that matter here:
- An artifact you can execute or parse beats an artifact you have to
  believe. A manifest's `[dependencies]` outranks a README paragraph about
  dependencies, always.
- The ADR log is ground truth for *decisions*, not for *current behavior* —
  an accepted ADR whose implementation never shipped makes the docs
  aspirational, which is its own audit classification, not "accurate."

**2. Inventory the doc surface** — `scripts/inventory_docs.sh <TARGET_REPO>`
lists every tracked doc with a drift signal: when it last changed, and how
many commits have landed on non-doc files since. Then
`scripts/check_references.py <TARGET_REPO>` settles the mechanically
checkable half — relative links, heading anchors, backticked repo paths,
and paths named inside shell code blocks, each resolved against the working
tree. Both surface candidates; neither renders a verdict on prose. A clean
`check_references.py` run means nothing about whether the docs are *true*.

**3. Audit & report** — one row per finding in `docs-audit.md` (format:
`references/docs-audit-format.md`), each classified:
- **stale** — the doc makes a claim the repo contradicts *right now*
  (documented flag no longer exists, wrong directory name, superseded
  command, dependency list that doesn't match the manifest).
- **missing** — the repo does something real that no doc mentions (a whole
  script, a new category folder, a required env var, a behavior change).
- **orphaned** — the doc describes something removed; the text now points
  at nothing.
- **aspirational** — the doc describes intent that never shipped, written
  in the present tense as if it had. Distinct from stale: nothing regressed,
  it was never true.
- **unverifiable** — a claim about something outside the repo (a deploy
  target, an external service, a policy) that nothing in the tree can
  confirm or refute. Logged, not silently kept or silently cut.
- **accurate** — checked and confirmed. Log these too; a re-run shouldn't
  re-litigate claims someone already verified.

Report this before touching anything — it's the checkpoint. In
**interactive** harness mode (default), nothing in step 4 starts without the
user picking rows. In **auto** mode, `stale` and `orphaned` rows whose
ground truth is mechanically verifiable, plus every broken link/path from
step 2, proceed without waiting; `aspirational`, `unverifiable`, and any row
where the code looks wrong always pause — see "Harness mode."

**4. Act, per approved row, batched by doc file** — branch, edit, PR against
the default branch, `scripts/watch_and_merge.sh`, merge commit on green CI,
sync. Same mechanics as `parity-loop` step 3, with three docs-specific
constraints:
- **One PR per doc file or per coherent theme** — a twelve-file
  simultaneous rewrite is an unreviewable diff, which defeats the point of
  routing this through PR review at all.
- **Every claim you write must be checkable against something in the tree.**
  If you can't point at the manifest line, the script, or the code path that
  makes a sentence true, don't write the sentence.
- File one tracking issue per audit run (`assets/templates/issue-body.md`,
  labeled `docs-drift`) rather than one per row — a docs run produces
  dozens of small rows, and an issue each is ceremony with no traceability
  gain. The audit table goes in the issue body; each PR closes it with
  `Closes #N` once the last approved row is done. If the target has
  `RELEASE_NOTES.md`, add the dated entry before opening the PR.

**5. Verify** — re-run both step 2 scripts against the updated docs, and
actually execute the read-only commands the docs tell a reader to run
(`--help`, `--dry-run`, a test invocation, a build) rather than eyeballing
them. A documented command that errors is the most common single defect
this loop finds, and it is the one nobody catches by reading. Never run a
documented command that writes, deploys, publishes, or spends money to
"verify" it — mark those `unverified-by-design` in the report and say so.
Then re-audit: report before/after counts by classification, and what's
still open.

**6. Wrap-up retro** — regardless of how the run ended (all rows fixed, some
deferred, stopped mid-way), run a `meta/skill-retro` pass on `docs-loop`
itself, grounded in this run: did step 1's ground-truth order hold up, did
step 3's six classifications fit what this repo actually had, did step 5's
verification catch anything the audit missed? Read-only, safe to run
unattended in either harness mode — applying anything `skill-retro` finds is
a separate, explicitly-approved follow-up.

## Harness mode

Checked once at the start of step 4: the `LOOP_HARNESS_MODE` environment
variable. `auto` permits proceeding straight through the step-3 checkpoint
for rows where the correction is *transcription from a verifiable source*
rather than a judgment call:
- **stale** rows whose ground truth is a manifest value, a path, a command
  name, a flag, or a directory layout — the doc is being made to match a
  fact the tree already states.
- **orphaned** rows pointing at something demonstrably absent.
- Broken links, dead anchors, and missing paths from `check_references.py`.

Unset or any other value means **interactive** — the existing checkpoint
behavior, unchanged.

Auto mode does **not** touch any of the following; they pause and report
regardless of harness setting:
- **Any row where the CODE looks wrong rather than the doc.** This is the
  one that matters most — see Rules.
- **aspirational** rows — whether unshipped intent gets cut, kept as a
  roadmap note, or built is a product decision, not a docs edit.
- **unverifiable** rows — nothing in the tree can settle them, so no
  unattended pass should pretend to.
- Deleting a whole doc file, or editing anything in the ADR log.
- Rewriting ARCHITECTURE's boundary table, design rationale, or a stated
  Non-goal — those encode decisions, and a decision changing is news, not
  drift.
- Red CI past the one fix-up attempt (see Stop conditions).

## Stop conditions

- Every approved row from step 3 is resolved and step 5's re-audit is clean
  → done; report what remains under `unverifiable` and `aspirational`.
- User says stop, in chat or (headless mode) via a `.docs-loop-stop` file at
  the repo root, checked each iteration — honored in both harness modes.
- A PR's CI stays red after one fix-up attempt → pause on that row, leave
  the PR open, report it; never force a merge or skip ahead silently.
- A doc/code contradiction where the code is the suspect party → stop that
  row, report it, keep going on the rest. Don't block the whole run on one.
- **Interactive mode**: a row not explicitly approved stays in the report,
  not the loop. **Auto mode**: this applies only to the categories listed
  under "Harness mode."

## Rules

- **Ground truth before prose, every run.** Step 1 precedes step 2 for a
  reason; reversing them turns an audit into a proofread.
- **This loop never edits code.** When the docs and the code disagree, the
  code is authoritative for *what currently happens* — but that is not the
  same as the code being *right*. If the documented behavior looks like the
  intended one (a doc'd validation the code skips, an error path the code
  swallowed, a default that changed by accident), that's a bug found by
  reading, and the most valuable thing this loop produces. File it as an
  issue and hand it back — never "fix" the doc to match a bug, and never
  patch the code inside a docs PR.
- **Never invent capability.** No documenting a plan, a TODO, or a
  half-merged branch in the present tense. If it isn't in the tree, it isn't
  in the docs.
- **Don't sanitize honesty.** Limitations, Non-goals, "still open", and
  known-gap sections are deliberate in these repos. Update them for accuracy;
  never smooth them into marketing copy, and never delete a limitation
  because it's unflattering rather than because it's fixed.
- **CHANGELOG.md and RELEASE_NOTES.md are historical logs, not drift
  targets.** A past entry that's now outdated is *correct history*. Add new
  entries; never retroactively rewrite old ones.
- **ADRs are append-only.** A superseded decision gets a new superseding ADR,
  never an edit to the original record.
- Same standing workflow as the sibling loops: every change lands through a
  PR against the default branch, never a direct push; merge with a **merge
  commit** on green CI, never squash or rebase-merge.
- Keep the target's `RELEASE_NOTES.md` current if it has one — one entry per
  merged change from this loop.
- An `accurate` or `unverifiable` row is a logged decision, not an absence of
  one — don't let it silently vanish from the report on a re-run.
- Check `references/development-standards.md` before asserting a
  documentation requirement as this skill's own opinion — if either standards
  repo specifies one, cite the `ATLAS-###` ID or doc section instead.

## Limitations

- The mechanical half (`check_references.py`) covers links, anchors, and
  paths — the claims a machine can settle. Prose accuracy is judgment, and
  a clean script run is not evidence the docs are true. Most real drift is
  invisible to it. One structural false-positive class survives its
  resolution rules: a doc describing a *different* component's or repo's
  layout (which is most of this repo's own skills) names paths that
  correctly don't exist here. And it resolves against the working tree as it
  stands, so gitignored build output being present or absent changes some
  rows — run it on a clean tree.
- `historical-*` rows are reported but must never be acted on as drift. A
  path in a past `CHANGELOG`/`RELEASE_NOTES` entry that no longer resolves
  is usually the log doing its job — the entry recording a file's removal.
  The script labels them; the Rules above are what actually forbid the edit.
- The drift signal in `inventory_docs.sh` is commit recency, not semantics.
  A doc untouched for a year can be perfectly accurate, and a doc edited
  yesterday can be wrong — it ranks candidates for attention, nothing more.
- Doc-comment review is limited to the public API surface by default.
  Auditing every private-item comment in a large codebase is a different,
  much larger job, and worth scoping explicitly rather than assuming.
- Claims about anything outside the repo — deploy targets, infrastructure,
  external services, org policy — land in `unverifiable` and stay there.
  This loop can flag them for a human; it can't check them.
- Generated API reference output is out of scope. If rustdoc/Sphinx output is
  stale, the fix belongs in the source comments or the build, not here.
- It doesn't decide *what should be documented*. Coverage judgment (does this
  repo need a tutorial? an FAQ?) is the user's call — this loop reports what
  exists, what's wrong, and what's undocumented but real.

## Scripts

| Script | Purpose | Args |
| --- | --- | --- |
| `inventory_docs.sh` | Lists tracked docs with a drift signal (last changed, code commits since) | `[target-dir] [--limit N] [--include-untracked]` |
| `check_references.py` | Resolves every relative link, heading anchor, backticked repo path, and shell-block path against the working tree | `<repo-root> [doc ...] [--all] [--strict]` |
| `watch_and_merge.sh` | Waits for a PR's CI, merges (merge commit) + syncs on green, retries once on a transient watch failure — identical to `parity-loop`'s copy | `<pr-number> [--retries N] [--repo <owner/repo>]` |

All three use `git`/`gh` and the Python standard library only — no extra
dependencies. They resolve paths relative to their own location, so they run
whether this skill is installed or just checked out locally.
