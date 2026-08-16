# Release Notes

skill-retro lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/meta/skill-retro) —
this log tracks commits against `main`, same convention as
[parity-loop's RELEASE_NOTES.md](../../my_loops/parity-loop/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.2.1 — YAML-safe description
**2026-08-16**

- **Fixed ([#59](https://github.com/baileyrd/skill_pack/issues/59)):** the
  frontmatter `description` was an unquoted plain scalar containing `": "`,
  which is invalid YAML — a colon-space inside a plain scalar reads as the start
  of a nested mapping. It is now a `>-` block scalar. The *value* is byte-for-byte
  unchanged; this is a representation fix, verified by round-tripping the parsed
  string before and after.
- **Why it went unnoticed:** `scripts/check_repo.py` parses frontmatter with a
  hand-rolled line-based parser that tolerates the construct, so CI stayed green
  and packaging worked, while anything using a real YAML parser rejected the file
  outright. `quick_validate.py` was the instance that surfaced it. The repo was
  validating with a parser more permissive than its consumers'.

---

## v1.2.0 — A third disposition for findings, plus two step-ordering fixes
**2026-08-16**

From this skill's own step 6 self-retro, during a run against
`meta/my-skill-creator` (which was itself invoked to draft
`dev_practices/unix-philosophy`). All three findings came out of the same
run and each traces to a concrete incident in it.

- **Added (S1):** step 5 now names **recording a finding as an issue** as a
  third disposition alongside applied and declined, and the Status enum in
  `references/retro-findings-format.md` gains `filed (#N)`. The retro that
  found this had all seven of its findings filed as issues rather than
  applied — a legitimate and probably common outcome that the skill had no
  vocabulary for, leaving every row's Status undefined. The entry is
  explicit that a filed finding gets **no** version bump or `RELEASE_NOTES.md`
  entry on the target, since nothing about it changed yet, and that a
  part-applied/part-filed batch should say which is which rather than
  implying the whole table landed.
- **Changed (S2):** the pointer to `references/retro-findings-format.md`
  moved from step 4 into step 3. The pointer existed, but only after step 3
  had already classified every finding — so the table's shape felt settled
  before its required columns were known. That's exactly what happened on
  this run: the first table shipped without the File/Section and Status
  columns and had to be redone.
- **Changed (S3):** the severity definitions now call out a case they
  under-rated — a finding that puts a **false statement into a user-facing
  artifact** rates at least `costly-guess` even when this run was unharmed.
  The axis otherwise reads as "how bad was the guess *during* the run,"
  which mis-sorts a generated report that confidently printed "3 runs each
  per configuration" when there had been one. Nothing went wrong during that
  run; the cost lands on whoever reads the artifact and believes it.

---

## v1.1.2 — Description under claude.ai's upload limit
**2026-08-16**

- **Fixed:** the `description` was 1135 characters, over the 1024-character
  limit claude.ai enforces on skill upload, so the zip was rejected outright.
  Trimmed to 1009 (15 characters of headroom) with every trigger phrase kept —
  the cuts are the "through the normal PR workflow" tail, already covered by
  the versioning convention it cites. Nothing about what the skill does
  changed.
- **Context:** five skills here shipped over the limit at once, and none of the
  local tooling noticed: `install_skills.py` copies frontmatter without reading
  it, `build_skill_zips.py` zips it the same way, and Claude Code itself loads
  an over-length description fine. Only claude.ai rejects it, at upload, one
  file at a time. `check_repo.py`'s `manifests` check now enforces the limit so
  this fails locally and in CI instead.

## v1.1.1 — `redundant-step` covers two shapes, not one
**2026-08-15**

- **Fixed:** step 3's category list gave `redundant-step` no definition, and
  the name pushes toward deletion. Applied from this skill's own step-6
  self-retro, run after a `docs-loop` retro where a finding didn't fit: the
  tracking-issue step there wasn't redundant at all — it was **correct when
  auditing and fixing are split, and stated unconditionally**. The fix was a
  condition, not a cut. `redundant-step` was used anyway because nothing
  better existed, which is how a taxonomy gap turns into a wrong proposed
  edit.
- `redundant-step` now explicitly covers both shapes, with a warning not to
  let the category's name push toward cutting a step that's right half the
  time. `references/retro-findings-format.md` cross-references it.
- **Two sibling findings from the same self-retro were logged and not
  applied** — step 0's assumption that B's run is a discrete "just finished"
  block (it spanned eight turns with unrelated work interleaved), and the
  findings format having nowhere to record a rule that *fired and prevented*
  a defect. Both `cosmetic`, both single-run evidence; per this skill's own
  Limitations, one occurrence of a minor finding is worth logging rather than
  necessarily acting on. They'll be worth doing if a second run hits them.

## v1.1.0 — Wire skill-retro into its own wrap-up (step 6, self-retro)
**2026-08-13**

- **Added:** step 6, "Self-retro" — after finishing a retro run on some
  other skill B (step 5), `skill-retro` turns the same lens on itself,
  grounded in how *this run* actually went (did step 0's evidence
  identification have friction, did a finding fail to fit step 3's
  categories, did the findings-table format need a column this run
  actually needed, did an approved edit apply more messily than expected).
  Reported as its own separate findings table, same read-only-before-write
  discipline and explicit-approval gate as every other target.
- **Guarded against recursion:** step 6 only fires when this run's B was
  some *other* skill — a direct self-retro invocation (B already =
  `skill-retro`) doesn't trigger a second self-retro pass on top of the one
  that just ran.
- Mirrors the same wiring pattern used for `my_loops/rust-migration` v1.1.0
  (a one-line addition to a target skill's own wrap-up), applied here to
  `skill-retro` checking itself rather than a sibling skill inviting it in.

## v1.0.0 — Initial release
**2026-08-13**

- **Added:** first cut of the skill. Introduces the `meta/` category —
  tooling about this repo's own skills, distinct from `my_loops/`
  (Rusty-Mill platform maintenance) and `yt_research_for_cc/` (YouTube
  pipeline).
- **Core mechanism:** an evidence-grounded, single-run retrospective on a
  target skill's own `SKILL.md`/`references/`/`scripts/` — reconstructs
  what actually happened against the skill's stated steps (skipped/
  reordered steps, questions that should have been pre-answered by the
  instructions, guesses made where the text ran out, stale references,
  broken scripts), classifies each as a category/severity finding with a
  concrete proposed edit, reports before writing anything, and only
  applies approved edits — followed by a version bump and
  `RELEASE_NOTES.md` entry on the target skill, through this repo's normal
  PR workflow. Never auto-applies, never fabricates a finding with no
  concrete incident behind it.
- Explicitly does not wire itself into anything automatically (no hook, no
  auto-invoke at the end of another skill's run) — that's flagged as a
  deliberate follow-up decision, not bundled into this initial cut.
- No `scripts/` — this skill is a reading/judgment/writing pass; it shells
  out to nothing beyond the `git`/`gh` any other change in this repo
  already needs for its PR.
