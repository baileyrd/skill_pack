# Phase 14 — Synthesis

Read the complete `findings.json`, write the audit report and the
prioritized backlog, and present them.

This phase doesn't run any new probes. It transforms the dimension data
that earlier phases recorded into two markdown deliverables.

---

## Inputs

- `findings.json` — the audit's accumulated state.
- `assets/report-template.md` — the report skeleton.
- `references/verdict-rubric.md` — for re-checking severity edge cases.

---

## Step 1 — Sanity check findings.json

Before generating output, verify:

- `target`, `shellType`, `startedAt` are populated.
- Every dimension that wasn't deliberately skipped has a `verdict`.
- Every Critical / High finding has `evidence` non-empty and a
  `remediation` field. (If not, walk back and complete those entries —
  the backlog is unusable without remediation guidance.)
- Severity tally is consistent: count `findings.severity` across all
  dimensions.

If anything is missing, either re-enter the phase that produced the gap
or, if intentional (probe unavailable, source missing), set
`confidence: "low"` and document the limitation in the methodology
section.

Update `findings.completedAt` and the `report.verdictCounts` /
`report.severityCounts` fields.

---

## Step 2 — Generate `audit-report.md`

Open `assets/report-template.md` and fill it in. The sections are:

1. **Header** — target name, paths, shell type, audit period, scope.
2. **Executive summary** — 2-3 paragraphs describing the overall shape
   of the shell, headline counts (Critical / High), and the single
   most important architectural observation. Write it for someone who
   has 60 seconds.
3. **Verdict summary table** — one row per dimension with verdict,
   finding count, and top severity. Skipped dimensions show
   `Skipped — <reason>`.
4. **Verdict + severity totals** — Pass/Warn/Fail/Unknown counts and
   Critical/High/Medium/Low counts.
5. **Architecture observations** — a narrative section where you call
   out cross-dimensional patterns the per-dimension write-ups would
   miss. For example:
   - "Theming and persistence both rely on un-namespaced localStorage
     keys (08-T-03 and 13-P-01 are really one underlying gap)."
   - "The shell's error boundary placement (Phase 06) explains why
     plugin failures can't be surfaced cleanly (Phase 10)."
   - "Multi-window state sync (Phase 12) and persistence schema
     versioning (Phase 13) will both be required for the planned
     workspace feature."
   - Aim for 3–6 observations. Skip this section only if the audit is
     unusually narrow.
6. **Per-dimension findings** — one section per dimension. For each:
   - Verdict + 1-3 sentences of rationale.
   - Evidence list (file paths, probe names, screenshots).
   - Findings table: ID / Severity / Title (full write-up lives in the
     backlog).
   - Skipped dimensions get a one-line note.
7. **Methodology notes** — what was probed, what tools were used, what
   couldn't be probed and why. Be honest about confidence.
8. **Appendix A** — `staticInventory` summary.
9. **Appendix B** — pointers to probe outputs (saved files).

Save to `/mnt/user-data/outputs/audit-report.md`.

---

## Step 3 — Generate `audit-backlog.md`

The backlog is a flat, ordered list of every finding across all
dimensions, ordered by severity then dimension index. Severity tiers:
Critical → High → Medium → Low. Within a tier, dimension order (03
layout → 13 persistence) so related items cluster.

Each backlog item gets a full write-up:

```markdown
### SH-014 — Deep links to /settings/billing 404 after auth refresh

- **Severity**: High
- **Dimension**: 04 Navigation & Routing
- **Scope**: All auth-gated routes when token is expired
- **Confidence**: high

**Description**

A direct URL load to `/settings/billing` during an expired-token state
redirects to `/login` but loses the original target. After login the
user lands on `/dashboard` instead of the requested page.

**Evidence**

- `/tmp/shell-audit/04-deeplink-trace.txt:18`
- `src/auth/redirect.ts:42`

**Remediation**

Capture the requested path before the auth redirect and append it as
a `?next=` query parameter. Restore it on successful login. Add a
test that exercises the round trip.

**Verdict contribution**

This finding is the primary driver of the Warn verdict for the
Navigation & Routing dimension.

---
```

Use this exact subsection template for every finding. Number them in
the order produced by the audit (the finding IDs are already
sequential — preserve them).

At the top of the backlog, put a one-table summary:

```markdown
# Audit Backlog — <target name>

| Tier     | Count |
|----------|-------|
| Critical | 0     |
| High     | 4     |
| Medium   | 11    |
| Low      | 6     |
| **Total**| **21**|

Top blockers (Critical + High):

1. SH-014 — Deep links to /settings/billing 404 after auth refresh (Navigation)
2. SH-021 — Modal close returns focus to body, not trigger (Accessibility)
3. SH-040 — Route transitions trigger 320ms long task (Performance)
4. SH-070 — Plugin failures swallowed silently (Extensibility)

---
```

Save to `/mnt/user-data/outputs/audit-backlog.md`.

---

## Step 4 — Present the deliverables

Use `present_files` to surface both deliverables to the user. Follow
with a *brief* summary. Don't repeat the report content — the user can
read it.

Example summary:

```
Audit complete.

Shell type:       desktop (Tauri 2.x + Next.js inside)
Verdict roll-up:  3 Pass · 6 Warn · 2 Fail
Severity totals:  0 Critical · 4 High · 11 Medium · 6 Low

Headline observations:
  • Strongest: theming & persistence (with a versioning gap to address now)
  • Weakest:   accessibility (focus mgmt) and multi-window state sync
  • Cross-cutting: 3 of the 4 High findings trace back to a single missing
    primitive — a global event bus the shell never grew

Both deliverables are in /mnt/user-data/outputs/. The backlog is the file
you'll want to import into your tracker.
```

---

## Step 5 — Wrap up

Update `findings.json`:

```json
"completedAt": "<ISO>",
"phasesCompleted": [
  "00-preparation", "01-static-scan", "02-runtime-bootstrap",
  "03-layout", "04-navigation", "05-accessibility", "06-state",
  "07-performance", "08-theming", "09-cross-platform",
  "10-extensibility", "11-observability", "12-multi-window",
  "13-persistence", "14-synthesis"
],
"report": {
  "reportPath": "/mnt/user-data/outputs/audit-report.md",
  "backlogPath": "/mnt/user-data/outputs/audit-backlog.md",
  "verdictCounts": { "Pass": 3, "Warn": 6, "Fail": 2, "Unknown": 0, "Skipped": 0 },
  "severityCounts": { "Critical": 0, "High": 4, "Medium": 11, "Low": 6 }
}
```

Save `findings.json` itself alongside the deliverables (it's the
machine-readable form of the audit and useful for follow-up automation):

- `/mnt/user-data/outputs/findings.json`

---

## Output of this phase

Three files in `/mnt/user-data/outputs/`:

1. `audit-report.md` — narrative report.
2. `audit-backlog.md` — prioritized issue list.
3. `findings.json` — full machine-readable record.

All presented via `present_files`.
