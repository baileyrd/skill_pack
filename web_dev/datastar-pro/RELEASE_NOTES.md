# Release Notes

datastar-pro lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/web_dev/datastar-pro) —
this log tracks commits against `main`, same convention as
[skill-retro's RELEASE_NOTES.md](../../meta/skill-retro/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.0.1 — Fix dead TOC anchor in core.md
**2026-08-15**

- **Fixed:** `references/core.md`'s table of contents linked
  `[Operators in Expressions](#operators-in-expressions)`. The heading it
  means is `### Operators`, which GitHub slugs to `#operators`, so the link
  went nowhere. The entry was also listed after `Action Calls` when the
  section it points at sits *before* it, under `## Expression Syntax`.
- **Fixed by:** pointing the entry at the real anchor (`[Operators](#operators)`)
  and moving it into document order. Fixed the TOC rather than renaming the
  heading — the heading is the content, the TOC is a pointer at it, and
  pointers yield to what they point at. Every other anchor in the file
  already resolved; this was the single wrong entry, not a systemic problem.
- **Found by:** `my_loops/docs-loop`'s first run against this repo
  ([#17](https://github.com/baileyrd/skill_pack/issues/17)). Worth noting
  for anyone re-running that checker against this skill: the finding only
  became visible after fixing the checker's own slug generation, which had
  been collapsing runs of whitespace and so reported 12 *correct* anchors in
  `references/styling.md` as broken. GitHub hyphenates each whitespace
  character, so `data-style — Reactive Inline Styles` is
  `#data-style--reactive-inline-styles`, with two hyphens.

## v1.0.0 — Imported from baileyrd/datastar-pro-skill
**2026-08-13**

- **Added:** reviewed and imported the audited v1.0 milestone of
  [`baileyrd/datastar-pro-skill`](https://github.com/baileyrd/datastar-pro-skill)
  — `SKILL.md` (273 lines, task-oriented routing table) + 6 reference
  modules (`core.md`, `backend.md`, `styling.md`, `components.md`,
  `rocket.md`, `architecture.md`, plus `stellar.md` — a 7th module added
  after the v1.0 milestone closed, not yet reflected in the source repo's
  own `.planning/PROJECT.md`, which still says "6 reference modules";
  worth a note back upstream, not fixed here since it's the source repo's
  own planning doc) + `evals/evals.json` (6 evals, 52 expectations).
- **Review findings**: the source repo's own `.planning/milestones/
  v1.0-AUDIT.md` had already found and the shipped state had already
  resolved all 3 flagged gaps before this import — confirmed by diffing
  the imported files against the audit's descriptions rather than
  re-finding them: README broken links (fixed), `styling.md` missing a
  TOC (present), evals 1 & 3's stale "CDN" wording (already corrected to
  "Datastar Pro script tag"). No open gaps carried over.
- **Deliberately excluded** from the import:
  - `datastar-pro-main/` — a 1.2MB vendored copy of the actual Datastar
    Pro library source. Its `LICENSE.md` is proprietary
    ("This software is proprietary and may only be used, copied,
    modified, or deployed by entities that have entered into a valid
    commercial license agreement... Redistribution... strictly
    prohibited without prior written consent") — copying it into
    `skill_pack` would be a redistribution of commercially-licensed
    source, not something this repo does regardless of what license
    `skill_pack` itself carries.
  - `CLAUDE.md` and `.planning/` — development-process scaffolding for
    working *on* the `datastar-pro-skill` repo itself (project charter,
    roadmap, phase plans, research notes), not part of the shipped
    skill's own instructions. `skill_pack`'s own conventions
    (`RELEASE_NOTES.md`, this file) serve the equivalent role going
    forward.
- **Maintenance model**: `skill_pack` is this skill's home from here —
  not a periodic sync target for `datastar-pro-skill` the way
  `yt_research_for_cc/notebooklm` is a live sync target for
  `notebooklm-py`. Future changes land and are versioned here directly.
  Confirmed, not just assumed: the user archived
  [`baileyrd/datastar-pro-skill`](https://github.com/baileyrd/datastar-pro-skill)
  on GitHub after this import (read-only, reversible) specifically so
  there's no ambiguity about which copy is authoritative.
- **Added per this repo's conventions**: `version: 1.0.0` frontmatter
  field (source repo's `SKILL.md` didn't carry one), a provenance note
  at the top of `SKILL.md` pointing back at the source repo and audit,
  and a "Wrap-up retro" closing section wiring `meta/skill-retro` into
  this skill's own wrap-up — the single-shot-utility shape (like
  `yt-search`), since this skill has no numbered `Run`/`Procedure` steps
  of its own to append a final step to.
- New `web_dev/` category folder — this skill doesn't fit `my_loops`
  (Rusty-Mill platform maintenance), `yt_research_for_cc` (YouTube
  pipeline), or `meta` (tooling about this repo's own skills). User
  confirmed a new category over a bare top-level skill directory when
  asked.
