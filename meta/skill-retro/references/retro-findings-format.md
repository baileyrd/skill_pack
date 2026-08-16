# Findings report format

Reported at the end of step 3, before anything gets edited. One table, one
row per finding that survived step 2's reconstruction (clean steps aren't
listed — this is a friction report, not a step-by-step recap).

| ID | Category | Severity | File / Section | What happened | Proposed edit | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F1 | ambiguous-instruction | costly-guess | `SKILL.md` step 5 | Step 5 says "adapt to this repo's conventions" with no fallback named when the target repo has no stated conventions of its own — had to invent a convention on the spot. | Add: "if the target repo states no conventions of its own, default to `Result`+`?`, no `unwrap()`/`expect()` outside tests, doc-comments — same fallback `parity-loop` already states." | proposed |
| F2 | missing-guardrail | could-have-caused-real-damage | `SKILL.md` step 3 | Step 3 lists "breaking-change" as a stop-and-ask but doesn't cover a capability whose fix needs a *new file format*, not a signature change — this run treated that as safe to auto-implement, which the author likely didn't intend. | Add "or introduces a new on-disk/wire format not already used by the target" to the breaking-change trigger list in step 3. | proposed |
| F3 | stale-reference | cosmetic | `references/platform-directory.md` | `rusty_foo` listed under `baileyrd` namespace, but `gh repo view` shows it moved to `Rusty-Mill` since this file was last updated. | Update the Namespace column for `rusty_foo`. | proposed |

Columns:
- **ID** — stable short ID (`F1`, `F2`, ...) for this report; doesn't need
  to survive across separate retro runs unless a log (below) is being kept.
- **Category** — one of `SKILL.md`'s step 3 categories:
  `ambiguous-instruction` / `missing-guardrail` / `stale-reference` /
  `redundant-step` / `tooling-bug` / `description-triggering` /
  `scope-drift`. Note `redundant-step` covers two shapes — a step that added
  nothing, and a step stated unconditionally that's only correct sometimes.
  The second takes a condition as its proposed edit, not a deletion; see
  `SKILL.md` step 3 for why the distinction matters.
- **Severity** — `cosmetic` / `costly-guess` / `could-have-caused-real-damage`,
  judged by what the gap could cause on a *different* run, not just how
  this run happened to turn out.
- **File / Section** — precise enough to open the file and find the spot —
  a step number, a reference file, a script's flag handling.
- **What happened** — the concrete incident from this run. No incident, no
  row — see `SKILL.md`'s Rules on not inventing findings.
- **Proposed edit** — the actual replacement text or a specific line/step
  change. Not optional; a finding without one isn't finished.
- **Status** — `proposed` (default, this report), `approved` (user signed
  off, about to be applied), `declined` (user said no, dropped from this
  run), `applied` (edited, versioned, and logged in the target skill's own
  `RELEASE_NOTES.md`), `filed (#N)` (recorded as an issue in the target
  skill's repo instead of being applied now — real, not dropped, but B is
  unchanged so it gets no version bump or `RELEASE_NOTES.md` entry until
  someone acts on the issue).

## Accumulating across runs (optional)

A single run's findings are single-run evidence — `SKILL.md`'s Limitations
section is explicit that one occurrence of a minor finding isn't
necessarily worth an edit on its own. For a skill retro'd repeatedly, it's
reasonable to keep a running `RETRO_LOG.md` next to the target skill's own
`RELEASE_NOTES.md` (not inside this skill's own directory — it belongs with
the skill being tracked) appending each run's findings table with a date
and run description, so a marginal finding that recurs across three
separate runs is visible as a pattern before someone decides to act on it.
This is a convention to offer the user, not something `skill-retro`
maintains unprompted — same "report, don't auto-write" discipline as
everything else here.
