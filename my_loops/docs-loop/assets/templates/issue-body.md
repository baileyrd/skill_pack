## Documentation drift

Audit run {{DATE}} against `{{COMMIT}}`. Scope: {{SCOPE}}
<!-- SCOPE: "whole repo" or what step 0 narrowed it to -->

**Findings:** {{N_STALE}} stale · {{N_MISSING}} missing · {{N_ORPHANED}} orphaned ·
{{N_ASPIRATIONAL}} aspirational · {{N_UNVERIFIABLE}} unverifiable · {{N_ACCURATE}} accurate

## Audit

{{AUDIT_TABLE}}
<!-- The docs-audit.md table, findings only — accurate rows can stay in the
     file without cluttering the issue. -->

## Needs a decision

{{STOP_AND_ASK}}
<!-- Rows that never auto-apply: the code looks wrong rather than the doc,
     aspirational claims, unverifiable claims, ADR/boundary/Non-goal edits.
     "none" if there are none. -->

## Acceptance

- [ ] Every approved row's doc edit merged (grouped per doc file / theme,
      one PR each — not one twelve-file rewrite)
- [ ] Every new claim traceable to something in the tree — a manifest line,
      a path, a script, a workflow step
- [ ] `check_references.py` clean on the changed docs
- [ ] Read-only documented commands actually executed, not eyeballed;
      write/deploy/publish commands marked unverified-by-design
- [ ] `RELEASE_NOTES.md` entry added (if the repo has one)
- [ ] Rows under "Needs a decision" answered or explicitly deferred — not
      silently closed with the rest

<!--
Filed by the docs-loop skill from docs-audit.md — one issue per audit run,
not per row, since a docs run produces many small findings and an issue each
is ceremony without traceability gain. Each doc PR closes this issue only
once the last approved row is done.

docs-loop edits documentation only. Any row here where the CODE is the
suspect party belongs in its own issue against the code — never fixed inside
a docs PR, and never resolved by rewording the doc to match the bug.
-->
