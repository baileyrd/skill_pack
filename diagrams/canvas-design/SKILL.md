---
name: canvas-design
description: >-
  Creates original, gallery-quality static visual art as a single PNG or PDF
  by first writing a short design philosophy (an invented art movement) and
  then expressing it on a canvas with code - form, color, composition and
  sparse typography doing the communicating, not paragraphs. Use this skill
  whenever the user asks for a poster, print, album or book cover, art piece,
  abstract or generative artwork, visual identity piece, flyer, or any other
  one-off static design meant to be looked at, including asks like "make me a
  poster for my band", "design some wall art about entropy" or "create a
  cover for this zine". Not for UI screens, diagrams of systems, charts, or
  slide decks.
license: Apache-2.0 (LICENSE.txt). Bundled fonts are SIL OFL 1.1 (assets/fonts/*-OFL.txt).
compatibility: Needs python3 with Pillow (PNG) or reportlab (PDF); matplotlib or cairo also work.
metadata:
  version: "1.0.0"
---

# Canvas Design

Two outputs: a design philosophy (`.md`) and the artwork it produces (one
`.png` or `.pdf`, more pages only when asked). The work must be original —
never imitate a living artist's signature style or copy existing artwork.

## 1. Write the philosophy

Invent a movement and write its manifesto, so the canvas has a rulebook rather
than a subject to illustrate.

- **Name** it in 1–2 words ("Chromatic Silence", "Brutalist Joy").
- **4–6 tight paragraphs** on how it shows up through space and form, color
  and material, scale and rhythm, composition, and hierarchy. Say each point
  once.
- Keep it general — don't name the user's topic; the topic enters in step 2.
- Specific about direction, loose enough to leave interpretive room.

Example, condensed: **"Geometric Silence"** — pure order and restraint.
Grid-based precision, stark graphics, dramatic negative space; type small and
exact, large quiet zones; Swiss formalism meets material honesty. Structure
communicates, not words.

Save it as `<movement-name>.md`.

## 2. Hide the subject in the work

Pick the conceptual thread from the request and embed it as a quiet reference
— in a proportion, a palette, a count, a rhythm — that someone who knows the
subject will feel and anyone else reads as strong abstract composition. Even
for a game, film or band, aim for art, not a cartoon or illustration of it.

## 3. Make the canvas

Write a script that renders the piece; code gives the precision a hand-drawn
look can't.

- **Visual first, ~90/10.** Repetition, accumulated marks, layered patterns and
  exact geometry, in a limited, deliberate palette. A useful default register:
  the look of a field study from an imaginary discipline — systematic markers,
  sparse clinical labels — applied to something intangible.
- **Type as a design element.** Usually thin and small; bold only where the
  context calls for it (a punk show poster, not a ceramics studio). Fonts in
  [assets/fonts/](assets/fonts/): Crimson Pro (serif, incl. italic), Instrument
  Sans, JetBrains Mono, IBM Plex Mono, Big Shoulders, Italiana, Gloock,
  Boldonse. Load them by path; other installed fonts are fine too.
- **Containment is non-negotiable.** Everything inside the canvas with real
  margins; nothing overlaps or clips unless the overlap is the idea. Measure
  text extents rather than guessing.

## 4. Refine, don't add

Render, look at the output image, and do a second pass. The instinct to add a
shape, filter or font is usually wrong — tighten spacing, alignment, color and
proportion of what's already there until it reads as deliberate and finished.
Check again for clipping and collisions after every change.

Deliver the image plus the philosophy `.md`.

## Multiple pages

When asked for more, treat page one as the opening spread of a book: each
further page is a distinct variation on the same philosophy, together
suggesting a quiet narrative. Bundle into one PDF or a numbered PNG set.

## Wrap-up retro

After delivering, run a `meta/skill-retro` pass on this skill grounded in the
run: did the philosophy actually constrain the canvas, did containment checks
catch clipping, did the refine pass improve or just add? Reporting is
automatic and safe; applying any finding is a separate, approved change.
