# Release Notes

Reverse chronological, one entry per meaningful change.

---

## v1.0.0 — Initial skill
**2026-11-16**

- **New:** writes a tailored image prompt for a character turnaround sheet
  from a reference image or text description. Built from a prompt Nano
  supplied; that prompt survives nearly verbatim as
  `assets/prompt-generic.md`, the no-reference fallback.
- **Tailoring:** `assets/prompt-template.md` replaces the source prompt's
  three-way style conditional with the one detected style and adds a
  visible-traits block. Unseen traits are marked for the model to infer,
  never invented, and the prompt states that the image outranks the text.
- **Added to the source prompt:** a left/right asymmetry line, a neutral
  full-body pose, and "no text, labels or watermarks", three places
  turnaround sheets commonly drift.
- **Layout:** seven views by default, overridable; the panel count is
  rechecked after any change.
- **Scope:** emits a prompt only. No image-generation call, no model
  variants, no script; the check is five lines the model runs itself.
- Opens the `image_prompts/` category. Eval-Kit suite with four cases.
