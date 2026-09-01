# MERGE-PROPOSAL.md format

Written at the end of step 3 (mergeable clusters only), before anything is
verified or reported. One file per cluster, written to the scratch proposal
location (`references/merge-proposal-format.md`'s own directory naming: see
SKILL.md step 3) — never into either candidate's real path.

## Header

```markdown
# Merge proposal: <cluster name>

Candidates:
- `<label-a>` — `<path-a>`
- `<label-b>` — `<path-b>`

Classification: mergeable — complementary | mergeable — conflicting

Proposed merged source: `<scratch-path>/<file(s)>`
```

## What each candidate does

One paragraph per candidate: its purpose, its structure, how
complete/tested it looks (own test suite? edge cases handled? any doc-
comment caveats about known gaps, e.g. "not constant-time"). This is the
evidence the coverage table and the conflict-resolution section below draw
on — write it from having read the actual source, not from
`coverage_matrix.py`'s 60-character doc preview.

## Coverage table — every item, no exceptions

One row per **normalized item name** from `scripts/coverage_matrix.py`'s
output across the candidates — every row that tool produced, not a
selection. This table is the mechanism behind the "never silently drop"
rule: an item with no row here, or a row with an empty **Resolution**
cell, is exactly the failure this skill exists to prevent.

| Item | Kind | In | Resolution |
| --- | --- | --- | --- |
| `hmac_sha256` | fn | both | Merged — `rusty_oauth`'s signature, `rusty_rdp`'s internal padding-length precomputation (faster on repeated calls with the same key) |
| `constant_time_eq` | fn | `rusty_oauth` only | Kept from `rusty_oauth` — `rusty_rdp`'s HMAC verification currently uses `==`; carrying this over closes a real timing-side-channel gap in the merge, not just a feature parity gap |
| `hmac_md5` / `hmac_sha1` | fn | `rusty_rdp` only | **Dropped** — MD5/SHA-1 HMAC variants are specific to `rusty_rdp`'s NTLM/CredSSP protocol needs, out of scope for a general HMAC-SHA256 module; `rusty_rdp` keeps its own `hmac_md5`/`hmac_sha1` locally rather than folding protocol-specific hash variants into the merged crate |

Resolution is one of, stated explicitly per row:
- **Kept from `<label>`** — carried over as-is (or trivially adapted) from
  one candidate, the other candidate had no equivalent or a strictly
  weaker one.
- **Merged** — synthesized from both; say what was taken from each.
- **Dropped — `<reason>`** — the only acceptable way for an item to not
  appear in the proposed source. A reason that amounts to "wasn't needed"
  without saying *why* it wasn't needed doesn't count — see SKILL.md
  step 3's rule.

A row's **In** column reproduces `coverage_matrix.py`'s own answer
(`both`, or the single label that has it) — don't hand-summarize it, since
step 4's verification re-runs the tool and diffs against this table
mechanically.

## Conflicts and resolution (mergeable — conflicting only)

For a cluster classified `mergeable — conflicting`, one entry per genuine
behavioral conflict (not just a naming or structural difference): what each
candidate does differently, which behavior the merge adopts and why, and
whether the other behavior is still reachable (a parameter/mode) or is a
real, stated tradeoff. This is the same "surface the behavioral question,
don't silently pick a winner" discipline `dedupe-loop` step 4.1 applies —
here already resolved with a stated reason, since this skill actually
proposes the merge rather than only flagging the question.

## Verification

Which candidate(s)' own existing test suite was run against the proposed
merged source (step 4), and the result — pass/fail, and for any failure,
whether the proposal was adjusted or the regression is a stated, accepted
tradeoff (never silent). "Not run — no reachable test suite for this
candidate" is a valid entry, not a gap to hide.

## Recommended host location

Which candidate's location (or a new one) the merge should eventually land
in, and why — a recommendation for the human reviewer, not a decision this
skill makes. Note anything the other candidate's callers would need to
change (import path, feature flag) if this recommendation is taken.
