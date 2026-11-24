---
name: character-sheet
description: >-
  Writes a tailored, model-agnostic image prompt for a character turnaround
  reference sheet: studies an uploaded reference image (or a text
  description), detects its rendering style, records only the traits that
  are actually visible, and fills a fixed prompt template so an image model
  redraws the same character in a multi-view grid on white. The default is
  seven views (four head closeups: front, left profile, right profile, back;
  three full-body: front, side, back) and is overridable (expressions row,
  three-quarter view, prop callouts). Emits the prompt in one copyable block
  for pasting into any image model alongside the reference; it does not
  render the image. Use when the user asks for a "character sheet",
  "turnaround", "model sheet", "character reference sheet", "multi-view
  reference", "front side back views of this character", or wants a
  consistent character for animation, games, comics or AI video. Not for
  tabletop RPG stat sheets, written character bios, or drawing a diagram.
metadata:
  version: "1.0.0"
---

# Character sheet

The output is a prompt, not a picture. The user pastes it into an image
model together with the reference image, so the prompt has two jobs: pin
down what must not drift between views, and leave the image as the authority
for everything else.

## Rules that hold every run

- **Describe only what is visible.** A trait the reference does not show
  (the back of a jacket, a hidden hand, eye colour behind sunglasses) goes
  in the prompt as "not visible in the reference; infer it consistently
  with the visible design", never as an invented detail. An invented detail
  is treated by the image model as a requirement and overrides the image.
- **The image outranks the text.** The filled prompt says so in its own
  words (the template's last consistency line). Keep it.
- **One style, stated flatly.** Name the single style the reference uses.
  A three-way "if illustrated / if photoreal / if 3D" conditional is for the
  untailored fallback only; in a tailored prompt it invites style drift.
- **Features, not identity.** Describe a person by visible features. Do not
  name who a real person is from their face, and describe skin by colour
  and undertone rather than a guessed ethnicity. A character the user names
  themselves may be named.
- **Counts must agree.** The number of views named in the layout equals the
  number stated in the quality section. Recount after any layout change.

## Procedure

1. **Find the reference.** An attached image: look at it. A text
   description only: use it as the trait source and say the user should
   still attach an image if they have one. Neither: emit the fallback
   (step 5) rather than asking, and say what tailoring would add.
2. **Classify the style** as one of: illustrated (name the method:
   cel-shaded, flat vector, painterly, ink sketch, anime, pixel art),
   photorealistic, or 3D render (stylized or realistic). Note line weight,
   shading method and palette character in a phrase each.
3. **Record the traits** under the template's headings: build and
   proportions, face, skin, hair, eyes, distinguishing marks, outfit piece
   by piece with colour and material, accessories and props. Plain colour
   words a model renders reliably ("deep teal", "burnt orange"), no hex
   codes. Skip a heading the reference gives nothing for, except to mark a
   plainly relevant trait as not visible.
4. **Fill** [`assets/prompt-template.md`](assets/prompt-template.md): read
   it, replace every `{{slot}}`, delete the guidance comments. Apply a
   layout override if the user asked for one, per "Layout overrides".
5. **Fallback, no reference at all:** emit
   [`assets/prompt-generic.md`](assets/prompt-generic.md) unchanged apart
   from any layout override.
6. **Check, and fix before sending:** no `{{` left; view count agrees in
   both places; exactly one style named (tailored prompts); every "not
   visible" trait is marked rather than filled in; no real person named.
7. **Deliver** in this shape, in the reply (write a file only if asked):

   ````
   <one line: what the reference is and the style detected>

   ```text
   <the full prompt>
   ```

   Attach the same reference image when you paste this.
   Not visible in the reference, left to the model: <list, or "nothing">.
   ````

## Layout overrides

The default grid is the seven views above. When the user changes it:

- Keep rows of equal-sized panels and name every panel in order, left to
  right; image models follow an enumerated list better than "add a few
  expressions".
- Common additions: a three-quarter head view (insert after "front
  facing"); an expressions row (name each expression, same head angle); a
  prop or detail callout row (name each item); an outfit-variation row
  (state that face, hair and build stay fixed).
- More than about twelve panels degrades per-panel detail in current image
  models. Say so and suggest splitting into two sheets, then do what the
  user decides.
- A non-white background or dramatic lighting defeats the sheet's purpose
  as a reference; comply if asked, and note the trade-off in one line.

## Wrap-up retro

After delivering the prompt, run a `meta/skill-retro` pass on
`character-sheet` itself, grounded in this invocation: did the style
classification in step 2 fit the reference or need a class the list lacks,
did step 3's headings miss a trait the reference plainly carried, did a
layout override break the count check in step 6, did the user have to
correct an invented detail? Read-only and safe to run unattended; applying
anything `skill-retro` finds is a separate, explicitly-approved follow-up.
Skip it when the run only emitted the unchanged fallback.
