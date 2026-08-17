# Verdict Rubric

Two scoring axes are used in this audit:

1. **Dimension verdict** — Pass / Warn / Fail per dimension
2. **Finding severity** — Critical / High / Medium / Low per individual issue

The dimension verdict is a summary of all findings within that dimension.
Severity ranks individual issues in the prioritized backlog.

---

## Dimension Verdicts

### Pass

The dimension is in good shape. The shell exhibits the expected
architectural shape for its framework and shell type, and runtime probes
confirm it. Minor polish items may exist but no Critical or High findings.

A dimension passes when **all** of the following are true:

- No Critical findings.
- No High findings.
- At most three Medium findings, all with clear ownership-light remediation.
- Static evidence and runtime evidence agree.

### Warn

The dimension is mostly working but has real defects worth addressing
before the next significant change to the shell. The team can ship and
operate, but each new feature pays interest on the existing debt.

A dimension is Warn when **any** of:

- Exactly one High finding.
- Four or more Medium findings.
- A Medium finding with broad scope (affects every page / every panel /
  every theme).
- Static and runtime evidence disagree on a non-trivial point.

### Fail

The dimension has serious problems and should be remediated before
significant new work in the shell. The shell is fragile, hostile to users,
or violates a hard invariant of the chosen framework or platform.

A dimension is Fail when **any** of:

- Any Critical finding.
- Two or more High findings.
- A High finding combined with structural inability to remediate (e.g., the
  framework choice itself precludes a fix).

When a dimension cannot be evaluated (probes unavailable, source missing,
etc.) record it as `verdict: "Unknown"` with `reason: "<why>"` rather than
guessing.

---

## Finding Severity

Severity drives backlog ordering. Use these definitions consistently across
dimensions.

### Critical

The shell is broken, unusable for a class of users, or actively hostile.
Examples:

- The app cannot be navigated by keyboard at all (a11y).
- Closing the last window quits the app silently with unsaved data on
  desktop (multi-window / persistence).
- A theme switch leaves the shell in an unreadable state.
- The shell crashes the renderer / process on a common interaction.
- A persisted layout corruption locks users out on next launch.
- Shell-level XSS or unsafe extension execution path.

Critical findings *should not be deferred*. They block release of new
shell-touching changes.

### High

A major functional or architectural defect with clear user impact, or a
structural violation of the chosen framework's invariants. Examples:

- Deep linking is broken — direct URLs don't restore state.
- The command palette can't reach half the shell's actions.
- Window resize jank visible on every layout change.
- Design tokens exist but are bypassed by hard-coded colors throughout the
  shell.
- The plugin slot system can't isolate failure (one plugin crashes the
  shell).
- Focus is lost on every modal close (a11y).

High findings should be on the next sprint's backlog at the latest.

### Medium

A real defect with limited blast radius, or architectural drift that
will compound. Examples:

- Loading state inconsistency between sidebar and main pane.
- One panel ignores the persisted size on relaunch.
- A subset of menu items lack keyboard shortcuts.
- Telemetry covers most of the shell but misses the command palette.
- Dark mode is correct everywhere except settings.

### Low

Polish, consistency, or nice-to-have. Examples:

- Tooltip delay is inconsistent across regions.
- Icon sizes vary by 1–2px in adjacent toolbars.
- A debug menu is shipped to production but gated by a key combo.
- Inline doc strings are missing on shell-level components.

---

## Severity Decision Heuristics

When stuck between two adjacent levels, ask in order:

1. **Does it block users entirely?** → Critical.
2. **Does it block a meaningful workflow or violate a hard contract?**
   → High.
3. **Will it hurt if left for a quarter?** Yes → Medium. No → Low.
4. **Is the scope wide (every page / every theme / every persisted
   field)?** Bump up one level.
5. **Is remediation trivial (a one-line fix)?** Drop one level only if the
   user impact is also low; never drop Critical or High solely for ease of
   fix.

---

## Mapping Verdicts to Backlog

The Phase 14 synthesis produces a single ordered backlog. Each backlog item
records:

```json
{
  "id": "SH-014",
  "dimension": "navigation",
  "severity": "High",
  "title": "Deep links to /settings/billing 404 after auth refresh",
  "evidence": ["nav-trace.json#step-4", "screenshot-12.png"],
  "remediation": "Restore the route after token refresh in router guard.",
  "verdictContribution": "High → contributes to Fail verdict for navigation"
}
```

Backlog ordering: Critical first (in dimension order), then High, Medium,
Low. Within a severity tier, order by dimension index (03 layout → 13
persistence) so related items cluster.
