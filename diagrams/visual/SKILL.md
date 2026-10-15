---
name: visual
description: >-
  Turns the current work into one self-contained HTML page with inline SVG diagrams, no build step and no CDN. A
  data.json written from git facts and the files read is injected into a template by scripts/visual.py, then
  audited in headless Chrome for edge crossings, label overlap and text overflow. Modes are recap (what a branch
  changed, hunks pulled from git), plan (a drafted plan as a picture, read-only), explore (a folder, endpoint set
  or architecture), and map (a zoomable drill-down map of a skill pack or system). Use when the user runs /visual
  or asks to visualise, picture, diagram or visually recap a branch, PR, diff, plan or codebase area, or to map a
  skill pack's lanes, scripts and hooks. Sibling to fireworks-tech-graph, which draws one standalone diagram.
version: 1.0.1
compatibility: Needs git and Python 3 (stdlib only). The self-check screenshots need headless Chrome; pass --no-check without it.
---

# /visual

One command, one page. You write a `data.json`; `scripts/visual.py render` injects it into `assets/template.html`, which draws everything inline (SVG diagrams, file map, diffs) with no build step and no runtime CDN. Paths below are relative to this skill's folder; run the script from inside the project being visualised.

## Pick the mode

An argument wins: `/visual recap [base]`, `/visual plan [file]`, `/visual map [skills-dir or map.json]`, `/visual <path or thing>` (explore).

With no argument, run `python3 scripts/visual.py detect` and take the first that holds:

1. A plan was drafted in this conversation and not yet built → **plan**, from that text.
2. `suggested` is `recap` (branch ahead of base, or uncommitted changes) → **recap**.
3. `planCandidates` is non-empty → **plan**, from the newest one.
4. Otherwise → **explore** the current folder.

Say the chosen mode and its source in one line, then keep going.

## Run it

1. **Gather.** Recap: `python3 scripts/visual.py facts [--base REF]`, then read `git diff <mergeBase>` once, in order, taking notes; scope is the whole work unit of this conversation. Plan: read the plan and the real files it names. Explore: read the target; hand wide sweeps to a sub-agent.
2. **Write `data.json`** in the scratchpad, following `references/schema.md` and the section bar in `references/sections.md`.
3. **Render:** `python3 scripts/visual.py render data.json`. It prints `{"out", "bytes", "missingHunks", "check"}` and opens the page (`--no-open` on a headless box). `--out` takes a file or a directory. Without Chrome, `check` reports `skipped` and exits 0: say in the reply that the audit did not run. Fix each missing hunk (wrong path or `contains`) and re-render.
4. **Check.** `render` runs `visual.py check` in headless Chrome: light and dark screenshots (plus one drilled-in view for a map), and an audit of every diagram or view: edge crossings, edges sharing a line, labels lying on a line or a node, and text overflowing its box (`check.counts`). Exit 2 means a problem: move nodes (`col`/`row`, or a view `layout`), cut edges a view does not need, shorten labels, and re-render. Read the PNGs it lists; a broken diagram or empty section means fix and re-render. `--no-check` skips it; `--shots DIR` picks where the PNGs go.
5. **Reply** with the path, the mode, and a 1–3 line gist. Offer to publish it as an Artifact (the page is fully inline); publish only on a yes.

## Map mode: a drill-down map

For a skill pack or any system with nested levels. The page is a clean flowchart, light first with a dark mode: one top bar (breadcrumbs, ⌘K search over nodes and views, theme, export, keys), a column browser of views on the left, the map in the middle, and a short details strip under it (header, then What · When · How · Links tabs). Wheel or pinch zooms, drag pans, the minimap moves the camera, a click opens the details, and double-click or Enter on a stacked node zooms into its inner view. Run-order views get swimlanes (Ask → Check → Fix → Finish …) when their parts name the phase. Breadcrumbs, Esc, and the browser back button go up; `#view=<id>&node=<id>` deep-links. On a phone the details become a bottom sheet.

1. **Skeleton.** `python3 scripts/visual.py skillmap <skills-dir> --deep --out map.json` reads SKILL.md frontmatter, `families.json`, `/skill` mentions, referenced scripts, and `hooks/settings-snippet.json`; `--deep` follows every external skill into the skills it triggers. Not a skill pack? Write `map.json` by hand.
2. **Enrich.** Read the skills and fill every node's `what`, `when`, `how`, and real `source` — the panel shows all four, so none stays empty. Main steps first: keep process views to roughly four to six columns, set `mainSteps: true`, and move scripts, state, and policies into a step’s child view. Every original node stays reachable. Hub views keep comb connectors. Mark outside skills `kind: external` with `author` (GitHub login) and add `authors`; `render` embeds their avatars. Fix edges and give each view a short `caption`. `references/schema.md` § Map model is the contract.
3. **Render:** `python3 scripts/visual.py render --map map.json`. It searches each view for a crossing-free layout and bakes it into the page, then runs the check. Publishing the page (GitHub Pages)? Add `--source-base https://github.com/OWNER/REPO/blob/main/` (and `--source-root <dir>` when the hosted repo is a subfolder) so Source links open the hosted file. Finish with steps 4–5 of Run it.

## Rules

- **Grounded:** in recap mode, files, `+/-`, and hunks come from git through `render` (`hunks[].file` + `contains`); hand-typed diff lines are for plan sketches only. Prose is the one free-text surface; label anything inferred as inferred.
- **Diagram first:** every page carries at least one diagram of the real mechanism — new endpoints, modules, data flow — with `change` flags on what moved. Columns follow the flow, rows hold peers.
- **Lean, not thin:** no boilerplate intro or "review the diff anyway" prose; every block says something specific about this change.
- **Secrets:** redact keys, tokens, and `.env` values in every block (`sk-•••`).
- **Plan is read-only:** make no source edits while planning.
- **Output** lands in a gitignored place: `_tmp/<date>-visual/` when the repo ignores `_tmp/`, else `.visual/` (self-ignoring). `--out` overrides.

## References

- `references/schema.md` — the `data.json` contract, diagram layout, and the map model; open before writing data.
- `references/sections.md` — per-mode section list and quality bar for recap, plan and explore; open before writing data. Map mode needs only `schema.md`.
- `THIRD_PARTY_NOTICES.md` — attribution: adapted from BuilderIO/skills (MIT); diagram style and viewer UX from tt-a1i/archify (MIT). Read only to answer a licence question.

## Wrap-up retro

After the page is delivered, run a [`meta/skill-retro`](../../meta/skill-retro) pass on `visual` itself, grounded in
this run: did `detect` pick the right mode, did the check flag real problems or noise, did a `references/` file get
opened that the body should have carried, did a schema field have to be guessed? Read-only and safe unattended;
applying what it finds is a separate, approved follow-up.
