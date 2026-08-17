# Shell UI Architecture Audit: {{ target.name }}

**Target**: {{ target.name }}
**Code path**: {{ target.codePath | default("—") }}
**Runtime**: {{ target.runtimeUrl | default("—") }}
**Shell type**: {{ shellType }}{% if shellTypeSecondary %} (secondary: {{ shellTypeSecondary | join(", ") }}){% endif %}
**Audit period**: {{ startedAt }} → {{ completedAt }}
**Scope**: {{ target.scope }}

---

## Executive Summary

> Two to three paragraphs describing the overall shape of the shell, the
> headline findings (Critical and High count, broad strokes), and the most
> important architectural observation. Written so a non-engineer reader can
> grasp the state of the shell in 60 seconds.

---

## Verdict Summary

| Dimension                 | Verdict | # Findings | Top severity |
|---------------------------|---------|------------|--------------|
| 03 Layout & Composition   | {{ ... }} | {{ ... }} | {{ ... }} |
| 04 Navigation & Routing   |         |            |              |
| 05 Accessibility          |         |            |              |
| 06 State & Data Flow      |         |            |              |
| 07 Performance            |         |            |              |
| 08 Theming & Design Tokens|         |            |              |
| 09 Cross-Platform Parity  |         |            |              |
| 10 Extensibility          |         |            |              |
| 11 Observability          |         |            |              |
| 12 Multi-Window           |         |            |              |
| 13 Persistence            |         |            |              |

**Verdict counts**: Pass {{ counts.Pass }} · Warn {{ counts.Warn }} · Fail {{ counts.Fail }} · Unknown {{ counts.Unknown }}

**Severity totals**: Critical {{ s.Critical }} · High {{ s.High }} · Medium {{ s.Medium }} · Low {{ s.Low }}

---

## Architecture Observations

A short narrative section that synthesizes patterns across dimensions. For
example: "Theming and persistence both rely on `localStorage` keys that
aren't namespaced, which surfaces in two findings (08-T-03 and 13-P-01)
but is really one underlying gap." Use this section to call out cross-
dimensional themes the per-dimension write-ups miss.

---

## Per-Dimension Findings

For each dimension, write one section like the template below. Skip
"Skipped" dimensions but include a one-line note explaining why.

### 03 Layout & Composition — Verdict: {{ verdict }}

**Rationale**: 1–3 sentences explaining the verdict.

**Evidence**:
- File: `src/app/shell/Layout.tsx:42` — header / sidebar / main slot definitions
- Probe: `regionInventory` — captured live region rectangles ([attached](#))
- Screenshot: `screenshots/03-layout-default.png`

**Findings in this dimension**:

| ID     | Severity | Title                                          |
|--------|----------|------------------------------------------------|
| SH-001 | High     | Sidebar collapses below 1024px without state   |
| SH-002 | Medium   | Modal layer not portaled — z-index conflicts   |

(Each finding gets a full write-up in the Backlog file, linked by ID.)

---

### 04 Navigation & Routing — Verdict: {{ verdict }}

(repeat the template)

---

### 05 Accessibility — Verdict: {{ verdict }}

(repeat)

---

### 06 State & Data Flow — Verdict: {{ verdict }}

### 07 Performance — Verdict: {{ verdict }}

### 08 Theming & Design Tokens — Verdict: {{ verdict }}

### 09 Cross-Platform Parity — Verdict: {{ verdict }}

### 10 Extensibility — Verdict: {{ verdict }}

### 11 Observability — Verdict: {{ verdict }}

### 12 Multi-Window — Verdict: {{ verdict }}

> Skipped: not applicable to {{ shellType }} shell.   ← if applicable

### 13 Persistence — Verdict: {{ verdict }}

---

## Methodology Notes

- **Probes used**: web / desktop / cli pack from `references/`.
- **Tools**: list of tools used (DevTools, Playwright, asciinema, etc.).
- **Limitations**: anything that couldn't be probed and why (e.g., source
  maps not shipped, no second display available, no production telemetry
  access).
- **Confidence**: any dimension marked low-confidence and the reason.

---

## Appendix A — Static Inventory

Paste / summarize `findings.json#staticInventory`. Useful for readers who
want to verify the basis of the audit without re-running it.

---

## Appendix B — Probe Outputs

Either inline the most important probe results or link to attached files
(`probes/regionInventory.json`, `probes/tokenAudit.json`, etc.).
