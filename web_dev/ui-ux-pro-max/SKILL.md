---
name: ui-ux-pro-max
description: >-
  UI/UX design intelligence backed by a local, searchable database: 79 visual
  styles, 192 product-type palettes and reasoning profiles, 74 font pairings,
  119 UX and accessibility guidelines, chart, icon, GSAP motion and landing
  page patterns, plus stack-specific rules for 22 stacks (React, Next.js, Vue,
  Svelte, SwiftUI, Flutter, Tailwind, shadcn and more). Generates a coherent
  design system (style, colors, type, spacing, anti-patterns) for a new
  product or page. Use this skill whenever the task changes how an interface
  looks, feels, moves or is interacted with - designing or building a page,
  screen, component or dashboard, picking colors, fonts or spacing, reviewing
  UI for accessibility, contrast or responsiveness, fixing layout or animation
  bugs, or asks like "make this look professional", "design a landing page",
  "what palette fits a fintech app" or "audit this screen". Not for backend,
  API, infra or non-visual performance work.
compatibility: Requires python3 (standard library only) to run scripts/search.py.
metadata:
  version: "1.0.0"
---

# UI/UX Pro Max

Design guidance pulled from local CSV data by one search script. Results are
recommendations: the user and the repo's own rules win over them.

`$SKILL_DIR` is the folder containing this file. Always call the script by
full path with the interpreter named, since the install drops exec bits
(to run them directly instead: `chmod +x "$SKILL_DIR"/scripts/*.py`):

```bash
python3 "$SKILL_DIR/scripts/search.py" "<query>" [--design-system | --domain <d> | --stack <s>] [-n N]
```

## Priorities

Work top-down; the full rule text per category is in
[references/quick-reference.md](references/quick-reference.md) — read it for a
review/audit pass, not on every task.

| # | Category | Domain | Must have | Avoid |
|---|---|---|---|---|
| 1 | Accessibility | `ux` | Contrast 4.5:1, alt text, keyboard nav, labels | Removed focus rings, unlabeled icon buttons |
| 2 | Touch & interaction | `ux` | 44×44px targets, 8px gaps, loading feedback | Hover-only affordances, 0ms state changes |
| 3 | Performance | `ux` | WebP/AVIF, lazy load, reserved space (CLS < 0.1) | Layout thrashing |
| 4 | Style selection | `style`, `product` | Style matches product, SVG icons | Mixed flat/skeuomorphic, emoji as icons |
| 5 | Layout & responsive | `ux` | Mobile-first, viewport meta | Horizontal scroll, fixed px containers, disabled zoom |
| 6 | Typography & color | `typography`, `color` | 16px base, 1.5 line height, semantic tokens | <12px body, gray-on-gray, raw hex in components |
| 7 | Animation | `ux`, `gsap` | Meaningful, context-timed motion, reduced-motion | One duration everywhere, animating width/height |
| 8 | Forms & feedback | `ux` | Visible labels, errors at the field | Placeholder-as-label, errors only at top |
| 9 | Navigation | `ux` | Predictable back, ≤5 bottom-nav items, deep links | Overloaded nav |
| 10 | Charts & data | `chart` | Legends, tooltips, accessible colors | Color as the only signal |

## Workflow

1. **Read the request.** Product type, audience, style words, and the stack.
   Detect the stack from the project (`package.json`, `pubspec.yaml`,
   `Package.swift`, `composer.json`); if nothing is detectable and it matters,
   ask. A guessed stack misroutes every stack result.
2. **New product or page → design system.**
   `search.py "<product> <industry> <style words>" --design-system -p "Name"`
   returns pattern, style, palette, type, effects and anti-patterns. Optional
   1–10 dials: `--variance` (minimal ↔ bold), `--motion` (adds a GSAP snippet),
   `--density` (spacing scale; high for dashboards).
3. **Persist only when asked to keep it.** Add
   `--persist --output-dir "<project-root>"` (always pass the dir, or files land
   wherever the shell is). It writes `design-system/<slug>/MASTER.md` and, with
   `--page <name>`, `pages/<name>.md`, which overrides MASTER for that page. An
   existing MASTER is skipped; read it first, and use `--force` only with the
   user's say-so.
4. **Targeted concern → one domain.** Domains: `product style color typography
   chart ux landing icons gsap react web`. Auto-detection misroutes overlapping
   words, so pass `--domain` when results look off.
5. **Implementation → `--stack`.** `react nextjs vue svelte astro nuxtjs nuxt-ui
   angular laravel swiftui react-native flutter jetpack-compose html-tailwind
   shadcn threejs javafx wpf winui avalonia uno uwp`.
6. **Before delivering native/mobile app UI**, run the checklist in
   [references/pro-rules.md](references/pro-rules.md).

## Querying well

- One intent, 2–5 terms, one constraint: `"keyboard focus modal" --domain ux`,
  not a checklist.
- Search the UX outcome first, then the stack:
  `"badge chip label wraps" --domain ux`, then
  `"chip badge overflow nowrap" --stack html-tailwind`.
- Accessibility: one observable outcome per query (`"focus not obscured"`,
  `"icon button accessible label" --domain icons`); don't accept a generic hit
  for a specific WCAG criterion.
- RTL (Arabic, Hebrew, Persian, Urdu, `dir="rtl"`): add `--rtl` to `style` and
  `product` searches and honor `rtl_level` — `full` is safe, `partial` needs
  per-component checks, `caveats` encodes direction, so say so and offer a
  mirrorable alternative. `--rtl=full` keeps only the safe rows.
- Verify the top hit fits the product and platform before using it. Empty or
  off-topic: retry once, narrower or with an explicit domain. Still nothing:
  say no match was found and label what follows as general guidance. Never
  present a fallback as a database result or persist unverified output.
- Keep private project data out of queries.

Output: `-f ascii` (default), `-f markdown`, or `--json`.

## Wrap-up retro — design-system runs only

After a run that generated or persisted a design system (step 2–3), run a
`meta/skill-retro` pass on this skill grounded in that run: did the query
return a fitting style/palette on the first try, did auto-detection misroute,
did persistence behave? Skip it for single-domain lookups — a retro is out of
proportion to a one-query answer; run it there only if the user asks.
Reporting is automatic and safe; applying any finding is a separate,
approved change.
