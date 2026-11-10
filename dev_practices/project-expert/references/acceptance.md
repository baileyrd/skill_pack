# Acceptance checks

Run after the PR is open, before merge, from a fresh session on the branch with no local
setup. A same-session self-simulation is a weak test; use a separate agent (the expert must be reachable via the CLAUDE.md table and its
fallback). Pick real questions from this project's own sources.

| # | Ask the expert | Expect |
|---|---|---|
| 1 | A question a DECISIONS row answers directly (any row) | `ANSWER` + `SOURCE` naming that row |
| 2 | An implementation-detail question (naming, layout, error wording) | `TIER: default (logged D<n>)`, no escalation |
| 3 | A change that reverses a `[stated]` row (take a `[stated]` row that forbids something, "no X" or "never Y", and ask to add X) | `ESCALATE` with `REVERSES: D<n>` |
| 4 | Pass the user's answer back to the expert once | exactly one DECISIONS row and one `remind_me_add`; asking again adds neither |
| 5 | Inspect: nothing depends on a local plugin, mod or machine config | expert file and routing live in the repo |
| 6 | Read the PR body | lists every unsourced OPEN_QUESTIONS item and unreadable source |

Check 4 by counting rows before and after, and `remind_me_search` for the
decision. Post the results as a PR comment and `remind_me_add` them (tag
`smoke-test`). Do not merge checks 1-3 into one question; each tier is its own
failure mode.
