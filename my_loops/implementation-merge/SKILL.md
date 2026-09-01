---
name: implementation-merge
description: Merges 2+ candidate implementations of the same capability into one, combining the best of each rather than picking a winner — invoked after dedupe-loop/repo-inspector flags a convergent-but-diverged cluster where a straight pick-one isn't right. Determines mergeability first (reads each candidate, builds an item-by-item coverage matrix, classifies mergeable-complementary / mergeable-conflicting / not-mergeable — genuinely different-purpose tools stay separate). Dry-run only — produces a MERGE-PROPOSAL.md plus the proposed merged source at a scratch location, verified against each candidate's own test suite; nothing lands in either candidate's real path, no PR, no merge. Never silently drops an item from a losing candidate — every coverage-matrix item must resolve to kept, merged, or explicitly dropped with a reason. Trigger on requests to merge duplicate implementations, combine the best of two versions, or reconcile a dedupe-loop/repo-inspector convergent-but-diverged finding.
version: 1.1.0
---

# implementation-merge

Picks up exactly where `dedupe-loop`'s step 4.1 and `repo-inspector`'s
`convergent-but-diverged` classification stop: both of those skills
correctly refuse to silently pick a winner between two implementations of
the same capability, but neither actually attempts the merge — they hand
the behavioral question to a human and stop. This skill is what runs
*after* that hand-off, when the answer is "yes, combine them" rather than
"pick one" or "keep both, they're actually different things."

It takes a specific, already-identified cluster (2+ candidate locations —
crates, repos, modules, files — implementing overlapping capability) as
input, rather than scanning a target itself the way the loop skills do.
The candidates normally arrive as a `convergent-but-diverged` row from a
`dedupe-loop`/`repo-inspector` report, but the user can also just name two
implementations directly ("merge `rusty_oauth`'s and `rusty_rdp`'s
`BigUint` implementations").

**v1 is dry-run only**, same posture as `repo-inspector`: no code lands in
either candidate's real location, no branch, no PR, no merge. The run ends
at a proposal — `MERGE-PROPOSAL.md` plus a proposed merged source file at a
scratch location — for human review. Acting on it (actually landing the
merge somewhere real) is a separate, explicitly-approved follow-up.

Worked example throughout this file: `rusty_oauth`'s and `rusty_rdp`'s
independently hand-rolled `BigUint` (arbitrary-precision unsigned integer)
implementations, run end-to-end (not just described) while building this
skill — a real `repo-inspector` finding against `Rusty-Mill/rusty_mill`,
confirmed `mergeable — complementary` and verified 13/13 against both
crates' own test suites (see RELEASE_NOTES.md). `repo-inspector`'s original
report bundled this cluster together with "HMAC-SHA256" and "RSA public
key" under one row; re-reading the actual source for this run found the
HMAC-SHA256 part of that claim was wrong — `rusty_rdp`'s `hmac.rs`
implements `hmac_md5`/`hmac_sha1` only, no SHA-256 at all — one instance of
the more general point step 0 makes below about not trusting a bundled
cluster row at face value.

## Run (when invoked)

**0. Scope**
- **Tooling preflight**: `chmod +x scripts/*.sh scripts/*.py 2>/dev/null ||
  true` — same executable-bit gotcha every skill in this repo has to guard
  against ([baileyrd/skill_pack#1](https://github.com/baileyrd/skill_pack/issues/1)).
  Where the skill directory is read-only, name the interpreter instead
  (`bash scripts/extract_public_surface.sh`, `python3
  scripts/coverage_matrix.py`).
- **`CANDIDATES`** — 2 or more `<label>=<path>` pairs naming what's being
  merged. If the caller hands in a `dedupe-loop`/`repo-inspector` cluster
  row, its "candidate crates/repos" column plus each one's local
  name/module is exactly this — **but check by reading, not by row count,
  whether that row actually names one capability or several bundled
  together.** A cluster row can cover more than one distinct capability at
  once (confirmed in practice: a `repo-inspector` row labeled "hand-rolled
  crypto primitives" turned out to bundle three separate things — HMAC,
  RSA, `BigUint` — only one of which was actually mergeable-complementary
  on a close read). Run this skill once per genuinely separate capability
  rather than assuming one row means one `CANDIDATES` set. If a candidate's
  repo isn't checked out locally yet, clone it (or `add_repo`) before this
  step — this skill, like `repo-inspector`, has no clone step of its own.
- **Not every cluster handed to this skill turns out to be genuinely
  mergeable** — step 2 makes that call fresh, even if the caller already
  called it `convergent-but-diverged`. Don't skip step 2's read on the
  assumption the classification is already settled; that classification
  was made without necessarily reading every line, and this skill's whole
  value is reading closely enough to actually attempt the merge.
- No `repo-config` prerequisite, unlike the sibling loop skills — v1 never
  files an issue or opens a PR, so there's no template/RELEASE_NOTES
  convention this skill depends on the target having.

**1. Read and summarize each candidate** — for every `CANDIDATES` entry,
read the actual source (not a doc-comment preview) and note: what it does,
how complete/tested it looks (own test suite? edge cases handled? any
doc-comment caveat about a known gap — `rusty_oauth`'s `ecc.rs` module doc
stating plainly it isn't constant-time is exactly this kind of thing to
carry forward, not silently lose), and its overall structure/approach.

**2. Build the coverage matrix, then classify** — run
`scripts/extract_public_surface.sh <label>=<path> ...` for all candidates
into one index, then `scripts/coverage_matrix.py <index.tsv>` over it. This
prints **every** item (not just ones present in ≥2 candidates, unlike
`dedupe-loop`'s/`repo-inspector`'s `find_clusters.py`) with which
candidates have it and which don't — the raw material both for classifying
the cluster and, later, for step 3's coverage table. It surfaces the
comparison, it doesn't classify it — read the actual source behind every
row, especially the single-candidate ones, before deciding. Classify the
cluster as one of:
- **mergeable — complementary**: the core capability is functionally
  equivalent, and the differences are additive — one candidate does
  something the other doesn't, without contradicting what the other does.
  The `rusty_oauth`/`rusty_rdp` `BigUint` case is this: identical
  representation and core algorithms, but each has gaps the other fills —
  `rusty_rdp` has little-endian serialization (`from_bytes_le`/
  `to_bytes_le`, matching RDP's own wire format) and a zero-modulus guard
  in `modpow` that `rusty_oauth` lacks; `rusty_oauth` has `bit_length`/
  `compare` as public general-purpose ops that `rusty_rdp` only had
  private, differently-named equivalents of. No conflict — every
  difference is an item to carry forward, not a contradiction to resolve.
- **mergeable — conflicting**: same capability, but a genuine behavioral
  conflict exists (different error-handling contracts, incompatible
  assumptions, one panics where the other returns `Result`) — still worth
  merging, but the conflict is a real decision to surface and resolve
  explicitly in step 3, never silently picked.
- **not-mergeable**: the surface-level similarity that got this cluster
  flagged doesn't hold up under a real read — different-purpose tools that
  happen to share a name or a domain vocabulary (`repo-inspector`'s own
  report against `rusty_mill` found exactly this for `rusty-db-core`'s SQL
  *builder* types vs. `rusty_rusqlite`'s SQL *parser* types — same names,
  opposite data-flow direction, not a merge candidate). Say why, and stop
  here — no proposal gets written for a `not-mergeable` cluster.

**3. For mergeable clusters, write the proposal** — format:
`references/merge-proposal-format.md`. Write the actual proposed merged
source to a scratch location (never into either candidate's real path —
e.g. `<scratch-dir>/<cluster-name>-merge-proposal/`). Don't assume a single
candidate becomes "the base" with the other's behavior patched in —
often there isn't a clean winner to build on top of. Synthesize per item
instead: for each row the coverage matrix produced, decide independently
which candidate's version to keep, whether to merge the two, or (rarer)
whether one item's implementation is simply better and should be adopted
even where the other candidate's overall structure is otherwise the
stronger base. A single candidate's structure *can* be the right starting
point when it clearly is — just don't default to it. The coverage table is
mandatory and exhaustive: **every row `coverage_matrix.py` produced for
this cluster must appear in the table with a resolution** — kept from one
candidate, merged from both, or dropped with a stated reason. A "wasn't
needed" reason without saying *why* it wasn't needed isn't a reason — see
Rules.

**4. Verify** — two required sub-steps, in order. Both are part of "done,"
not one required and one optional: the first run of this skill completed
step 4b (test-suite verification) and reported it as if step 4 were fully
done, having quietly skipped 4a — caught only in the wrap-up retro that
run's own step 6 required, when re-running 4a after the fact turned out
clean (no drop had actually happened), which was luck, not something 4b
established. Don't repeat that: 4a is not a formality bundled alongside
4b, it's the actual mechanism "never silently drop" depends on, and step 5
cannot be reported done without it.

**4a. Mechanical check (required, do this first).** Re-run
`scripts/extract_public_surface.sh` + `coverage_matrix.py` over `[the
candidates + the proposed merge's own source]` and confirm every item that
had a "kept"/"merged" resolution in step 3's table is actually present in
the proposal. This is the actual enforcement of "never silently drop" —
step 3's table is a claim; this is what checks the claim against the code
that was actually written, catching a table that says "merged" for
something the written code forgot.

**4b. Behavioral verification.** Where a candidate has a reachable test
suite, run it against the proposed merge (point the test file's imports at
the proposal, run `cargo test`/whatever the candidate's own test command
is) and report pass/fail per candidate. A failure means the proposal
doesn't yet honor that candidate's tested behavior — fix the proposal, or
write the regression into `MERGE-PROPOSAL.md`'s Verification section as a
stated, accepted tradeoff. Never silent either way.

**5. Report** — `MERGE-PROPOSAL.md` plus the scratch merged source are the
whole deliverable. **No code lands in either candidate's real location, no
branch, no PR, no merge.** Deliver both directly to whoever invoked the
run, the same way `repo-inspector` hands its report over — writing files
to a scratch location alone doesn't reach a human reviewer.

**6. Wrap-up retro** — regardless of how the run ended (a proposal written,
a cluster ruled `not-mergeable`, or stopped mid-way), run a
`meta/skill-retro` pass on `implementation-merge` itself, grounded in this
run: did step 2's mergeability classification hold up, did the coverage
table in step 3 actually catch everything, did step 4's verification
surface something the write-up missed? Read-only; applying anything found
is a separate, explicitly-approved follow-up. If instructions are followed
by reading this `SKILL.md` directly rather than through the `Skill` tool,
this step needs a deliberate self-check at the end of step 5 — the repo's
`retro_reminder.py` hook only fires on `Skill`-tool invocations.

## Stop conditions

- `MERGE-PROPOSAL.md` written and verified (step 4 run, pass/fail reported)
  → done.
- Cluster classified `not-mergeable` at step 2 → done, report why, no
  proposal written.
- Fewer than 2 reachable candidates (a named location doesn't exist, or a
  repo can't be checked out) → halt before step 1 and say what's missing.
- User says stop, in chat or (headless mode) via a
  `.implementation-merge-stop` file, checked before each step.

## Rules

- **Never silently drop an item.** Every row `coverage_matrix.py` produces
  for the cluster must resolve to kept, merged, or dropped-with-a-reason in
  `MERGE-PROPOSAL.md`'s coverage table — no exceptions, no "obviously not
  needed" without saying why. This is the one rule this skill exists to
  enforce; step 4 checks it mechanically, not just by eye.
- **v1 never writes into a candidate's real path, opens an issue, or files
  a PR.** The proposal is the entire output. A future version that lands
  an approved proposal is out of scope for this skill as written.
- A `mergeable — conflicting` cluster's behavioral conflict gets a stated
  resolution and reason in `MERGE-PROPOSAL.md`, never a silently-picked
  winner — same discipline `dedupe-loop` step 4.1 applies to the question
  it hands off; this skill resolves it explicitly instead of handing it
  off further.
- A cluster this skill rules `not-mergeable` is a real, logged outcome —
  say why, don't just quietly produce nothing.
- Don't trust the caller's `convergent-but-diverged` classification as
  already-settled — step 2 reclassifies from an actual read every time.

## Limitations

- Judgment-heavy code synthesis at its core — `coverage_matrix.py`
  mechanizes "did every item get accounted for," not the actual work of
  writing a good merged implementation. Treat the coverage table as a
  checklist this skill enforces, not evidence the merge itself is well
  designed.
- `extract_public_surface.sh` is Rust-specific (same `pub`/`pub(crate)`/
  `pub(super)` + `fn`/`struct`/`trait`/`enum` + doc-comment extraction as
  `repo-inspector`'s scripts) — a non-Rust cluster needs the comparison
  done by hand; the classification and proposal-writing steps themselves
  don't depend on the language.
- `coverage_matrix.py` only ever sees what `extract_public_surface.sh`
  extracted, which by design excludes fully **private** items (no `pub`
  qualifier at all) — they're invisible to any caller, so they're
  correctly out of scope for a *coverage* comparison. But a private
  helper can still represent a real design choice worth recording in
  `MERGE-PROPOSAL.md` even though no tool will ever flag it: confirmed in
  practice merging `rusty_oauth`'s/`rusty_rdp`'s `BigUint`, where dropping
  a private `divmod` helper (never public, but the subject of one of
  `rusty_oauth`'s own unit tests) needed a step 3 write-up and a step 4
  adapted-test note that no amount of running the coverage-matrix tooling
  would have produced on its own — step 1's "read the actual source"
  requirement is what catches this, not the scripts.
- Step 4's test verification is only as good as each candidate's own test
  suite — a behavior neither candidate tests can regress in the proposal
  without either script or the test run catching it.
- Doesn't decide *where* the merge ultimately lands (which candidate's
  location becomes the real one, or a new location entirely) — that's a
  recommendation in `MERGE-PROPOSAL.md`'s own format for the human review
  this hands off to, not something this skill resolves.
- No `LOOP_HARNESS_MODE`/auto mode, matching `repo-inspector` — there's no
  action step here to gate; every proposal is reviewed at the pace the
  reader chooses.

## Scripts

Neither script shells out to `gh` or clones anything — same as
`repo-inspector`, this skill's own steps never touch issues/PRs/CI. Both
require only `awk`/`find` (bash script) and `python3` stdlib (Python
script) — no third-party dependency.

| Script | Purpose | Args |
| --- | --- | --- |
| `extract_public_surface.sh` | Extracts module docs + public item signatures from N explicitly-named candidates (files or directories) into a flat, label-tagged index | `<label>=<path> [<label>=<path> ...] [--out <file>]` |
| `coverage_matrix.py` | Groups an index by normalized item name and shows **every** item (including single-candidate ones) with which candidates have it and which don't | `<index.tsv> [index2.tsv ...]` |

`extract_public_surface.sh` reuses `index_workspace_capabilities.sh`'s
extraction logic from `repo-inspector`, scoped down to an explicit
candidate list instead of a whole workspace's `cargo metadata` members —
this skill operates on one already-identified cluster, not a scan target,
so there's no workspace to enumerate. `coverage_matrix.py` reuses
`find_clusters.py`'s normalization but deliberately does **not** filter to
multi-candidate items the way that script does — a single-candidate row is
exactly what this skill's coverage table and "never silently drop" rule
need, not noise to discard.
