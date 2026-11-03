# Release Notes

Reverse chronological, one entry per meaningful change.

---

## v1.0.0 — Imported and rewritten
**2026-11-03**

- **Imported** from an upload of Anthropic's `canvas-design` example skill
  (Apache-2.0, `LICENSE.txt` kept). Modified as below; maintained here from
  now on.
- **Rewrote `SKILL.md`** from ~11.9 KB to ~4 KB as four numbered steps. Cut the
  repeated ALL-CAPS "masterpiece / countless hours" exhortations and the
  fabricated "the user ALREADY said it isn't perfect" line (a model follows a
  reason better than pressure, and a skill shouldn't put words in the user's
  mouth). Dropped "download whatever fonts are needed", which assumes network
  access. Added an explicit render-and-look check to the refine step.
- **Fonts:** kept 10 files across 8 families covering serif, sans, mono and
  display (~1 MB, each with its OFL text) of upstream's 54 (~5 MB), moved from
  `canvas-fonts/` to `assets/fonts/`. Instrument Serif was dropped because
  upstream shipped it without its license file.
- **Description** rewritten as a `>-` block naming concrete asks (poster,
  cover, wall art) and what it is not for (UI, system diagrams, charts,
  decks). Added `compatibility`, `metadata.version`, and a wrap-up retro.
