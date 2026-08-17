# Release Notes

fireworks-tech-graph lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/diagrams/fireworks-tech-graph) —
this log tracks commits against `main`: reverse chronological, one entry per
meaningful change, honest about what's still open.

---

## v1.0.0 — Imported into skill_pack
**2026-08-17**

Imported from [`yizhiyanhua-ai/fireworks-tech-graph`](https://github.com/yizhiyanhua-ai/fireworks-tech-graph)
(MIT, `LICENSE` retained) and maintained here from now on — this repo's own
versioned copy, not a live sync, same posture as `web_dev/datastar-pro`.

The diagram content is untouched: 15 diagram types, seven styles, the shape and
arrow vocabularies, layout rules, the UML coverage map, and all ten
`references/` files are exactly as shipped.

### Fixed on import

- **Every text file was CRLF — all three shell scripts were broken.**
  `validate-svg.sh` failed immediately with `$'\r': command not found` and
  `set: pipefail: invalid option name`. 20 of 20 text files converted to LF;
  the scripts run now, verified against a generated SVG. This is the exact
  failure `repo-config`'s `.gitattributes` exists to prevent, arriving in a
  skill upload — the repo's own `check_repo.py` `line-ends` check would have
  rejected the commit regardless.
- **No executable bits on any script**, while every invocation in `SKILL.md` is
  written `./scripts/…`. Bits set, and the recovery documented per this repo's
  convention ([#1](https://github.com/baileyrd/skill_pack/issues/1)) since the
  sync drops them again on delivery. `tests/test_script_invocation.py` enforces
  the note.

### Changed on import

- **Added `version: 1.0.0`** and this log, per repo convention.
- **Replaced the `Install Source` section** — it instructed the reader to
  install from upstream with `npx skills add … --force -g -y`. Running that
  over this copy would overwrite it with upstream and silently undo the
  line-ending fix, putting the shell scripts back to broken. Now a `Source`
  section recording provenance and saying not to re-install over the top. The
  `-y` in the original is the same flag removed from `meta/find-skills` on its
  import, for the same reason.
- **Added a `Requirements` section.** `rsvg-convert` is absent in this
  container and in many sandboxes. Workflow step 9 (PNG export) silently
  produces nothing without it, and the original said nothing about checking.
  The validator degrades correctly on its own (`⚠ Skipped`), which is good
  behavior worth documenting rather than discovering.
- **Extended the description** with the diagram-type list and the
  `rsvg-convert` caveat, keeping every original trigger phrase including the
  Chinese ones. 618 characters, under the 1024 limit.
- **Added a `Limitations` section**, which the original had none of. The
  load-bearing one: **validation checks structure, not meaning** — a diagram
  can be valid SVG and wrong, and every check still passes. Also that layout is
  rule-driven rather than solver-driven, so dense graphs need hand-adjustment,
  and that upstream is not tracked.

### Kept deliberately

- **`assets/samples/` — 1.5 MB of style-preview PNGs.** This makes the packaged
  zip roughly 1.6 MB against 85 KB for the largest existing skill. They're
  human-facing reference for choosing a style, not needed to generate anything,
  so they are the obvious cut if repo or zip size ever matters. Not cut now:
  discarding content from an upload is the user's call, not a silent import
  decision. `Limitations` says what they're for.
- **`agents/openai.yaml`** — a four-line display manifest for a different
  platform. Inert here; kept rather than pruned, on the same reasoning.

**Not evaluated.** No eval set or benchmark run. Verified by execution instead:
`generate-from-template.py` produced a valid 14.8 KB SVG from the bundled
`mem0-style1.json` fixture, and `validate-svg.sh` passed it after the
line-ending fix. Output quality across the seven styles is unmeasured.

**Category note:** opens a sixth category folder, `diagrams/`. The existing
five are scoped to external repo-maintenance loops (`my_loops/`),
skills as subject matter (`meta/`), a video-research pipeline
(`yt_research_for_cc/`), web-framework code generation (`web_dev/`), and design
discipline (`dev_practices/`) — none of which covers producing a diagram as the
deliverable. `ARCHITECTURE.md`'s Structure section and the root `README.md`
updated to match.
