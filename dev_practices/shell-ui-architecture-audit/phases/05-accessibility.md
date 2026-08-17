# Phase 05 — Accessibility

Audit the shell's accessibility: keyboard reachability, focus management,
ARIA / semantic landmarks, screen reader support, contrast, and motion
preferences. The shell sets the floor — if the shell fails on a11y,
every feature page inherits the failure.

---

## What we evaluate

| Concern               | Question                                           |
|-----------------------|----------------------------------------------------|
| Keyboard reachability | Is every interactive element reachable by keyboard alone? |
| Focus management      | Where does focus go on route change, modal open/close, async update? |
| Visible focus indicator | Is the focus ring always visible on focus?     |
| Landmarks             | Header / nav / main / aside / footer correctly roled or semantic? |
| Accessible names      | Every interactive element has a name (text, aria-label, aria-labelledby, title) |
| Live regions          | Async updates announced via aria-live where appropriate |
| Skip links            | "Skip to main content" available on every page    |
| Color contrast        | Text and meaningful UI meet WCAG AA              |
| Motion preferences    | `prefers-reduced-motion` respected for transitions |
| Resizable text        | Layout holds at 200% browser zoom                  |
| Screen reader rotor   | (TUI: not applicable; web/desktop: smoke test)    |

---

## Static probes

### Web

```bash
# Detect aria attribute usage breadth
rg -n 'aria-(label|labelledby|describedby|live|expanded|controls|hidden)' --type tsx --type vue --type svelte | wc -l

# Detect role usage
rg -n '\brole=' --type tsx --type vue --type svelte | wc -l

# Detect semantic landmarks vs div soup
rg -n '<(header|nav|main|aside|footer|section|article)' --type tsx --type vue --type svelte | wc -l

# Find focus management hooks
rg -n 'useFocusReturn|focus\(\)|setFocus|tabIndex|tabindex' --type tsx --type ts

# Find motion preference checks
rg -n 'prefers-reduced-motion|matchMedia.*reduce' --type tsx --type ts --type css

# Skip links
rg -n 'skip-to-main|Skip to' --type tsx --type vue --type svelte --type html
```

### Desktop

In addition to the web checks (the WebView is the same surface):

```bash
# Tauri menu accelerators
rg -n 'accelerator|Accelerator' src-tauri/

# Electron accelerators
rg -n 'accelerator:' --type ts --type js
```

### CLI / TUI

A11y in TUIs is mostly about: keyboard-only operation (always true by
definition), discoverable bindings, color contrast in the chosen palette,
and screen-reader compatibility of the host terminal (which is mostly the
terminal's responsibility, not the app's).

```bash
# Footer / status hint that lists active bindings
rg -n 'Footer|footer_hint|status_bar' --type py --type rust --type go

# Help screen / overlay
rg -n 'help_screen|Help|HelpScreen|F1\b|<F1>|ctrl-h' --type py --type rust --type go --type ts
```

---

## Runtime probes

### Web

From `references/runtime-probes-web.md`:

1. `ariaCoverage` — count interactive elements missing accessible names.
2. `focusTrap` — open a modal, tab through to confirm focus is trapped
   inside; close and confirm focus returns to the trigger.
3. `keyboardMap` — inventory declared key shortcuts.
4. **Manual keyboard tour**: Tab through the entire shell at the default
   viewport. Note:
   - Any element you can't reach.
   - Any element where the focus indicator is invisible.
   - Any focus jump that feels jarring (skipping ahead, looping back
     unexpectedly).
5. **Route-change focus**: navigate to a new route. Where does focus go?
   It should land on the page heading or main landmark, not be left on
   the previous link.
6. **Live-region check**: trigger a notification or async result. Is it
   announced? Search for `aria-live="polite"` near the toast / status
   region in DOM.
7. **Contrast** spot-check: use computed styles + `tokenAudit` results.
   For 5–10 representative text colors, compute contrast against their
   background. Below 4.5:1 = fail (3:1 for large text / non-text UI).
8. **`prefers-reduced-motion`**: open DevTools → Rendering → emulate
   `prefers-reduced-motion: reduce`. Trigger a route transition / modal
   open. Confirm motion is removed or substantially reduced.
9. **Zoom test**: set browser zoom to 200%. Confirm shell layout holds
   without overflow, content cut-off, or overlapping regions.

### Desktop

All web probes apply inside the WebView. Plus:

1. Native menu accelerators — verify each declared accelerator works
   (cross-check with `nativeMenuMap` from Phase 04).
2. Custom titlebar (if `decorations: false`): keyboard-resize and -move
   from window controls? (macOS: Ctrl+F2/F3 conventions; Windows:
   Alt+Space menu.)

### CLI / TUI

1. Confirm a footer hint or help screen lists every active binding for
   the current view.
2. Walk every binding manually; verify each works.
3. If the app uses color heavily, switch to a low-contrast theme (or run
   in a terminal with `TERM=dumb`) and confirm essential information is
   not color-dependent.
4. For Textual: run with the `--screenshot` flag or use the dev console
   to dump the widget tree and verify each focusable widget has a
   discoverable role.

---

## Verdict rubric

### Pass

- Every shell action reachable by keyboard.
- Focus indicator visible and consistent.
- Modals trap focus and return it.
- Route changes move focus to the new page heading or main.
- Landmarks present (header, nav, main, footer).
- All interactive elements have accessible names.
- Contrast meets WCAG AA on representative text/UI.
- Reduced-motion respected.
- 200% zoom holds.
- TUI: every binding discoverable in a help screen / footer hint.

### Warn

- A small number of unnamed interactive elements (≤ 3, all minor).
- Skip-to-main missing.
- Focus indicator hidden in one isolated component.
- Live regions missing on a non-critical async surface.

### Fail

- Any keyboard-unreachable shell action.
- Focus lost on every modal close / route change.
- Critical contrast failure (e.g., body text below 4.5:1 globally).
- Reduced-motion ignored on a strong vestibular trigger (large parallax,
  fast spin).

---

## Severity examples

- **Critical**: shell unusable without a mouse on the primary nav; or
  primary text fails contrast at 3:1.
- **High**: focus consistently lost on modal close; modal not trapped.
- **Medium**: skip link absent; live region missing on toast notifications.
- **Low**: tooltip lacks ARIA description; one edge-case element has no
  visible focus ring.

---

## Findings entry schema

```json
{
  "id": "05-accessibility",
  "name": "Accessibility",
  "verdict": "Fail",
  "verdictRationale": "Two High findings: focus lost on every modal close; sidebar collapse leaves no keyboard path to nav below 1024px (compounds with SH-001).",
  "evidence": [
    { "kind": "probe", "ref": "ariaCoverage", "summary": "8 interactive elements missing accessible names" },
    { "kind": "probe", "ref": "focusTrap", "summary": "Modal dialog does not trap focus" },
    { "kind": "log", "ref": "/tmp/shell-audit/05-keyboard-tour.txt" },
    { "kind": "screenshot", "ref": "/tmp/shell-audit/05-no-focus-ring.png" }
  ],
  "findings": [
    {
      "id": "SH-021",
      "title": "Modal close returns focus to document body, not the trigger",
      "severity": "High",
      "description": "Closing any modal via Escape or click-outside leaves `document.activeElement === document.body`. Keyboard users lose context and must Tab from scratch to resume.",
      "evidence": ["focusTrap probe output", "src/components/Modal.tsx:91"],
      "remediation": "Capture `document.activeElement` on modal open and call `.focus()` on it during the close handler.",
      "scope": "all modals",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

```
Phase 05 complete — Accessibility: Fail

Top issues:
  • [High] Focus lost on every modal close
  • [High] Sidebar collapse below 1024px has no keyboard alternative (compounds SH-001)
  • [Medium] 8 interactive elements missing accessible names
  • [Medium] Skip-to-main link absent

Findings recorded: 6 (2 High, 3 Medium, 1 Low)
Proceed to Phase 06 (State & Data Flow)?
```
