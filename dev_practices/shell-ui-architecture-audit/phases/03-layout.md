# Phase 03 — Layout & Composition

Audit the shell's outermost structure: regions and slots, density,
responsive behavior, modal / drawer / overlay layers, and how feature
content is composed into the frame.

---

## What we evaluate

| Concern              | Question to answer                                      |
|----------------------|---------------------------------------------------------|
| Regions              | Are header / nav / sidebar / main / footer well-defined and consistent? |
| Slots                | Does the shell expose composable slots, or hard-code each route's chrome? |
| Density              | Is there a single density mode, multiple, or accidental drift? |
| Responsive behavior  | How does the shell adapt across viewport / window sizes? |
| Modal / overlay layer| Where does it live in the tree? Z-index discipline? Portaling? |
| Composition seams    | Where do feature pages plug in? Is the seam consistent? |
| Empty frame          | What does the shell look like with no feature content? Crashes? Skeleton? |

---

## Static probes

### Repo-side checks

```bash
# Find the layout component (web/desktop)
rg -l 'Layout|Shell|AppFrame|RootLayout' src/ app/ components/ layouts/ \
  --type ts --type tsx --type vue --type svelte

# Find slot/portal references
rg -n 'createPortal|<Portal|<Teleport|teleport=' --type ts --type tsx --type vue

# Find density / density tokens
rg -n 'density|compact|comfortable|spacious' --type ts --type tsx --type css

# Tailwind responsive class usage
rg -n '(sm|md|lg|xl|2xl):' --type tsx --type vue --type svelte | wc -l

# Z-index inventory
rg -n 'z-index|z-\[|z-\d' --type css --type tsx
```

### Tauri / Electron specific

- `tauri.conf.json#tauri.windows[0]` for default size, min size, frame
  decoration mode, transparency.
- Electron `BrowserWindow` constructor — same fields.

### CLI / TUI specific

- Textual: read the `*.tcss` files. Look for `#header`, `#sidebar`,
  `#footer`, layout primitives (`Horizontal`, `Vertical`, `Grid`).
- Ratatui: search for `Layout::default().constraints(...)` calls.

---

## Runtime probes

### Web

From `references/runtime-probes-web.md`:

1. `regionInventory` — at the default viewport.
2. `regionInventory` again at 360 / 768 / 1024 / 1440 / 1920 widths
   (use `resize_window` between captures).
3. Trigger a modal, then re-run `regionInventory` to confirm modal-root
   placement.

### Desktop

1. `regionInventory` from the web pack inside the WebView.
2. `windowChromeAudit` from the desktop pack (chrome overhead, custom
   titlebar presence, min-size respect).
3. Resize the window to its declared min size and re-capture.
4. Maximize, then re-capture.

### CLI / TUI

1. Capture a screen at default terminal size (e.g., 100×30).
2. Capture again at small (80×24) and very small (60×20).
3. Capture at large (200×60).
4. For each capture, identify region boundaries from the rendered output
   and confirm against the `widgetTreeDump` from the runtime-probes-cli
   reference.

---

## Verdict rubric

Apply `references/verdict-rubric.md` plus these dimension-specific
heuristics.

### Pass criteria

- Regions are clearly defined in code (named slots, semantic landmarks)
  and consistent at runtime.
- Modal layer is portaled to a dedicated root (web) or implemented via a
  proper modal API (desktop / TUI).
- Responsive behavior is intentional and tested at standard breakpoints.
- Density is either one consistent mode or a deliberate set of modes
  selectable by the user.
- Z-index values come from a defined scale (tokens, constants), not
  scattered magic numbers.

### Common Warn signals

- Modal layer mounts inline rather than via a portal → z-index conflicts
  inevitable.
- Sidebar collapses on small viewports without a corresponding open/close
  affordance.
- One panel ignores density when others honor it.
- Z-index magic numbers ≥ 5 distinct values across the shell.

### Common Fail signals

- Layout breaks (overflow, content invisible, double scrollbars) at any
  in-spec viewport / window size.
- Modal locks the user out (focus trap broken, no close affordance, or
  underlying scroll bleeds through).
- Window cannot reach its declared min size without breaking.
- TUI renders unreadable at 80×24 (a baseline standard).

---

## Severity examples for this dimension

- **Critical**: shell breaks at a standard viewport / window size such
  that primary actions are unreachable.
- **High**: modal fails to portal and z-index conflicts hide actions in
  practice; or sidebar collapses without recovery affordance below 1024px.
- **Medium**: modal layer works but uses inline z-index magic numbers;
  density drift between two adjacent panels.
- **Low**: a pixel-level inconsistency between regions; a single tooltip
  positions slightly off-grid.

---

## Findings entry schema

Append to `findings.dimensions[]`:

```json
{
  "id": "03-layout",
  "name": "Layout & Composition",
  "verdict": "Warn",
  "verdictRationale": "Modal layer mounts inline; sidebar collapse below 1024 lacks recovery; otherwise sound.",
  "evidence": [
    { "kind": "file", "ref": "src/app/Shell.tsx:42-78", "summary": "Top-level region definition" },
    { "kind": "probe", "ref": "regionInventory@1920", "summary": "All regions present" },
    { "kind": "probe", "ref": "regionInventory@768", "summary": "Sidebar gone, no menu trigger" },
    { "kind": "screenshot", "ref": "/tmp/shell-audit/03-layout-768.png" }
  ],
  "findings": [
    {
      "id": "SH-001",
      "title": "Sidebar collapses below 1024px without a recovery trigger",
      "severity": "High",
      "description": "At viewports under 1024px the sidebar is hidden via `display: none` with no hamburger / drawer trigger. Primary navigation becomes unreachable on tablets and small laptops in split-screen.",
      "evidence": ["regionInventory@768", "/tmp/shell-audit/03-layout-768.png", "src/app/Shell.tsx:84"],
      "remediation": "Add a drawer/hamburger trigger that becomes visible below the sidebar's breakpoint, mounted in the header region.",
      "scope": "all routes, viewports < 1024px",
      "confidence": "high"
    },
    {
      "id": "SH-002",
      "title": "Modal layer renders inline rather than via a portal",
      "severity": "Medium",
      "description": "Modals are rendered as siblings of their trigger rather than at a dedicated modal root. Z-index conflicts have already required ad-hoc overrides in three components.",
      "evidence": ["src/components/Modal.tsx:12", "src/styles/overrides.css:88"],
      "remediation": "Introduce a `<ModalRoot />` near the document root and use `createPortal` to project modals into it.",
      "scope": "all modals",
      "confidence": "high"
    }
  ],
  "completedAt": "<ISO datetime>"
}
```

---

## Checkpoint

After scoring, print to the user:

```
Phase 03 complete — Layout & Composition: Warn

Top issues:
  • [High]   Sidebar collapses below 1024px with no recovery trigger
  • [Medium] Modal layer not portaled; z-index conflicts emerging

Findings recorded: 5 (1 High, 3 Medium, 1 Low)
Proceed to Phase 04 (Navigation)?
```

Wait for the user's response, then continue.
