---
name: dedupe-loop
description: Scans a set of platform repos for duplicate or near-duplicate implementations (e.g. every repo growing its own HTTP client wrapper) and proposes hoisting the genuine duplicates into a single common module on the platform layer, per the mechanism/policy split already established by ADR-011. Trigger on requests to find duplicated code across repos, consolidate common functionality, "do we have three versions of this," or hoist something into rustils/the platform layer. Companion to parity-loop and sovereignty-loop (same PR/CI/merge mechanics, same platform-repo scoping question) — checkpointed with per-cluster sign-off by default (this one spans repos, so a wrong call is costlier to unwind), but exact/near-duplicate clusters proceed unattended when `LOOP_HARNESS_MODE=auto`; a convergent-but-diverged cluster's behavioral question always still needs a human answer regardless of harness mode.
version: 1.1.2
---

# dedupe-loop

Finds capability areas that more than one platform repo has independently
built its own version of — HTTP clients, retry/backoff helpers, config
loaders, the usual suspects — and proposes hoisting the genuine duplicates
into one common module, the same "mechanism goes on the platform layer,
policy stays with the consumer" split that ADR-011 already established for
rust-shell's relationship to rustils. Worked example throughout: two repos
each with their own thin HTTP wrapper, hoisted into `rustils::net::http`.

This is the most invasive of the three sibling skills. `parity-loop` adds
capability inside one repo; `sovereignty-loop` swaps a dependency inside one
repo; this one changes the public surface of the hoist target *and* every
repo that adopts it — so nothing here is unattended, and the work itself
spans multiple repos, multiple PRs, and a real sequencing constraint (the
hoist target has to land before anyone can adopt it).

`assets/templates/` holds two issue-body templates — `hoist-issue.md` for
the module landing in the target repo, `adopt-issue.md` for each consumer —
copied into their respective TARGET repos, cross-linked by URL since GitHub
issues don't span repos natively.

## Run (when invoked)

**0. Scope**
- **repo-config prerequisite**: before acting on any approved cluster (step
  4), run `repo-config`'s `scripts/audit.sh` against `HOIST_TARGET` and
  every consuming repo that will get an adopt PR. Any repo scoring
  low/missing gets repo-config applied first — the hoist/adopt issue
  templates and RELEASE_NOTES convention assume it's there. Skip only if a
  prior step in the same session already confirmed a given repo.
- `PLATFORM_REPOS` — same scoping question as `sovereignty-loop`: propose a
  list spanning both `Rusty-Mill/*` and `baileyrd/rusty_*`
  (`references/platform-directory.md` has the current snapshot — migration
  between the two namespaces isn't complete, so check both), let the user
  narrow it. If a prior run already settled this for the same repo set,
  reuse it rather than re-asking.
- Development standards — `references/development-standards.md` points at
  the two external standards repos consulted before implementing a hoist
  (step 4.3 below), before falling back to generic conventions.
- `HOIST_TARGET` — which repo receives consolidated modules. Default to
  rustils (`rust-platform-core`), since it's the existing platform layer
  other repos already consume via ADR-011 — but confirm rather than assume;
  a genuinely UI- or domain-specific duplicate might belong somewhere else.
- `FOCUS` (optional) — narrow this run to one capability area (e.g. "http")
  instead of a full scan. Full scans on a large repo set take a while and
  produce a lot to review at once; a focused run is the better default when
  the user already has something specific in mind.
- Check `HOIST_TARGET`'s existing ADRs/RFCs for contracts already
  established (e.g. ADR-011 itself) so this skill doesn't propose re-doing
  an already-decided hoist — it's looking for *new*, not-yet-addressed
  duplication.

**1. Build a capability index per repo** — `scripts/index_capabilities.sh
<repo-path>` walks the repo's source tree and extracts module-level `//!`
doc comments plus public item signatures (`pub fn` / `pub struct` /
`pub trait` / `pub enum`) with their first doc line, one row per item. Run it
once per repo in `PLATFORM_REPOS`; this is mechanical extraction, not
judgment yet.

The argument is a **local path**, not a repo name — this skill has no clone
step, so any repo in `PLATFORM_REPOS` that isn't already checked out has to
be cloned first (`references/platform-directory.md` has the one-liner and
the namespace caveat).

**2. Cluster candidates across repos** — `scripts/find_clusters.py` takes
the combined indices and groups items by normalized name/keyword overlap
across *different* repos (single-repo matches aren't duplication — see
Rules). It surfaces candidate clusters, it doesn't classify them. Read each
cluster's actual source across the repos involved and judge:
- **exact/near-duplicate** — same functionality, reimplemented almost
  identically. Strong hoist candidate.
- **convergent-but-diverged** — same purpose, meaningfully different
  behavior (one repo's HTTP wrapper retries, another's doesn't; one supports
  a proxy, another doesn't). Still a hoist candidate, but the behavioral
  difference is a real decision — surface it, don't silently pick a winner.
- **coincidental-similarity** — similar names or keywords, different actual
  concerns (a `Client` for HTTP and a `Client` for a message queue). Not a
  hoist candidate — log why and move on.

**3. Report** — one row per cluster in `duplication-audit.md` (format:
`references/duplication-audit-format.md`): the capability, which repos have
their own copy, classification, behavioral differences if diverged,
reconciliation size (S/M/L/XL), and recommended hoist target. In
**interactive** harness mode (default), **nothing in step 4 starts without
the user picking which clusters to act on** — same hard checkpoint
`sovereignty-loop` has, for the same reason (toolchain/public API change)
plus one more: this spans repos, so a wrong call here is more expensive to
unwind than a single-repo swap. In **auto** harness mode (see "Harness
mode" below), **exact/near-duplicate** clusters proceed to step 4 without
waiting for a human pick; **convergent-but-diverged** clusters never
skip the behavioral question in step 4.1, in either mode.

## Harness mode

Checked once at the start of step 4: the `LOOP_HARNESS_MODE` environment
variable. `auto` permits proceeding straight through the step-3 checkpoint
for **exact/near-duplicate** clusters only — same functionality,
reimplemented near-identically, nothing to design-decide. Unset or any
other value means **interactive** — the existing checkpoint, unchanged.

Auto mode does **not** touch any of the following — they pause and report
regardless of harness setting:
- **convergent-but-diverged** clusters — the behavioral-difference question
  in step 4.1 is a real design decision (which behavior becomes default,
  does it become a parameter, does an outlier repo opt out); auto mode
  cannot answer it on the loop's own judgment.
- **coincidental-similarity** clusters — not a hoist candidate either way,
  logged and skipped, not something to "auto-act" on.
- Red CI past the one-attempt fix-up budget on either the hoist PR or an
  adoption PR (see Stop conditions).
- The step 0 scope questions (`PLATFORM_REPOS`, `HOIST_TARGET`, `FOCUS`) —
  auto mode changes what happens after classification, not whether scope
  gets defined. If step 0 can't be answered from the repos' own docs and no
  one's available to ask, halt and report what's blocking start.
- Sequencing still applies in auto mode exactly as in interactive: the
  hoist PR must merge before any adoption PR opens.

**4. Act, per approved cluster only:**
1. **Convergent-but-diverged clusters**: before writing any code, put the
   behavioral difference to the user as a real design question (which
   behavior becomes the default, does it become a parameter, does a repo
   with unusual needs stay opted out) — this is a "public API change"
   decision by the standing working agreement, not something to resolve by
   picking whichever repo's version looks more complete.
2. File the hoist issue in `HOIST_TARGET` (`assets/templates/hoist-issue.md`,
   labeled `dedupe-hoist`) and one adopt issue per consuming repo
   (`assets/templates/adopt-issue.md`, same label), each linking the others'
   URLs. This is the tracking trail `Closes #N` needs later, same
   convention as the sibling skills.
3. **Land the hoist first.** Check `references/development-standards.md`
   for an applicable requirement from either standards repo before writing
   the module — conform and cite the `ATLAS-###` ID or doc section if one
   applies. Implement the common module in `HOIST_TARGET` as pure mechanism
   — configurable where the clusters diverged, no repo-specific policy
   baked in (the ADR-011 split: mechanism on the platform layer, policy
   stays with the consumer). Test, PR against
   `HOIST_TARGET`'s default branch, `scripts/watch_and_merge.sh`, merge,
   sync. **Don't start any adoption work until this merges** — consumers
   have nothing to adopt yet.
4. **Then adopt, per consuming repo**, in any order: bump the pin to
   `HOIST_TARGET`'s new module (whatever mechanism the existing ADR-011-style
   contract already uses — git rev, path dependency, internal registry;
   this skill doesn't invent a new one), replace the local implementation
   with the hoisted module plus whatever thin policy layer stays local,
   delete the now-dead local code in the *same* PR (no orphaned duplicate
   left "just in case" — see Rules), test, PR, watch-and-merge, sync.
5. Once every approved consuming repo has adopted, close the tracking
   issues and note in the run summary which repos are done and which
   clusters were deferred.

**5. Wrap-up retro** — regardless of how the run ended (clusters fully
adopted, some deferred, or stopped mid-way), run a `meta/skill-retro` pass
on `dedupe-loop` itself, grounded in this run: did step 2's clustering and
classification (exact/near-duplicate vs. convergent-but-diverged vs.
coincidental-similarity) hold up, did a convergent-but-diverged behavioral
question in step 4.1 need something the instructions didn't cover, did the
hoist-then-adopt sequencing actually work as described? Read-only, safe to
run unattended in either harness mode — applying anything `skill-retro`
finds is a separate, explicitly-approved follow-up, not part of this run.

## Stop conditions

- All approved clusters fully adopted (hoist merged + every consumer's
  adoption PR merged) → done; report deferred/declined clusters.
- User says stop, in chat or (headless) via a `.dedupe-loop-stop` file at
  `HOIST_TARGET`'s root, checked each iteration — honored in both harness
  modes.
- A hoist-target PR's CI stays red after one fix-up attempt → pause the
  whole cluster (adoption can't start without it), report, don't skip ahead.
- A convergent-but-diverged cluster's behavioral question is still
  unanswered → that cluster stays at step 4.1, no code gets written for it,
  in either harness mode.

## Rules

- A cluster needs items from **at least two different repos** to count as
  duplication. One repo doing something on its own is just an
  implementation — don't manufacture a hoist candidate out of it.
- No auto-merge default in **interactive** mode — every cluster needs
  explicit sign-off before step 4, and a diverged cluster additionally needs
  its behavioral question answered before implementation starts. In **auto**
  mode (`LOOP_HARNESS_MODE=auto`), exact/near-duplicate clusters may proceed
  without a human pick; diverged clusters always still wait on the
  behavioral question — see "Harness mode."
- The hoist target's PR merges before any consumer's adoption PR opens.
  Sequencing isn't optional — an adoption PR with nothing to adopt yet isn't
  a real PR.
- Delete the local duplicate in the same PR that adopts the hoisted version.
  A leftover "just in case" copy is exactly the kind of duplication this
  skill exists to remove.
- Same standing workflow as the sibling skills: PR against default branch,
  never a direct push; merge with a **merge commit** on green CI, never
  squash/rebase. Keep `RELEASE_NOTES.md` current in every repo touched, if
  that repo has one.

## Limitations

- Cluster detection is keyword/structural matching plus judgment — it can
  miss duplication hiding under unrelated names, and it can surface
  coincidental matches that aren't real duplication. Treat step 2's output
  as a candidate list, same caveat as the sibling skills' search steps.
- Reconciling a convergent-but-diverged cluster is a design decision this
  skill surfaces, not one it resolves — expect step 4.1 to sometimes take
  longer than the implementation that follows it.
- Cross-repo sequencing means a cluster can't fully complete in one sitting
  the way a `parity-loop` issue can — the hoist PR has to merge before
  adoption PRs even start. Plan for a cluster to span more than one session.
- No clone path, deliberately: `index_capabilities.sh` reads a local
  directory and nothing here fetches a repo, so a `PLATFORM_REPOS` entry
  that isn't checked out is a manual `gh repo clone` before step 1. The
  sibling skills' `scan_platform_repos.sh` does this for them; porting it
  here would add a `gh` dependency this skill otherwise doesn't need, so
  it's a separate decision rather than an assumed gap.
- Assumes each consuming repo already has (or the user sets up) a pinning
  mechanism for depending on `HOIST_TARGET` — the ADR-011 precedent for
  rust-shell is the model to follow; this skill doesn't establish that
  contract from scratch for a repo that doesn't have one yet.

## Scripts

| Script | Purpose | Args |
| --- | --- | --- |
| `index_capabilities.sh` | Extracts module docs + public item signatures from one repo into a flat index | `<repo-path> [--out <file>]` |
| `find_clusters.py` | Groups indexed items by normalized name/keyword across repos, filters to clusters spanning ≥2 repos | `<index1.tsv> <index2.tsv> ...` |
| `watch_and_merge.sh` | Waits for a PR's CI, merges (merge commit) + syncs on green, retries once on red — identical to the sibling skills' copy | `<pr-number> [--retries N] [--repo <owner/repo>]` |
| `next_issue.sh` | Picks the next open, approved issue to work in a given repo, skipping `blocked`/`needs-human` | `[--label dedupe-hoist] [--repo <owner/repo>]` |

`find_clusters.py` is stdlib-only Python (no third-party dependency, in
keeping with the standing minimal-dependencies principle). Everything else
shells out to `gh`/`git` plus **`jq`**, which `next_issue.sh` pipes its `gh`
output through. No script here invokes `ripgrep` — an earlier version of this
line claimed it did.
