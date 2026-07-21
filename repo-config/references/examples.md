# Calibration examples

Excerpts only — enough to match tone and detail level, not full files to copy.
Full versions exist in the repo-standards examples if a complete reference is
needed. The two files worth hand-adapting (README, ARCHITECTURE) are the ones this
mostly matters for.

## ARCHITECTURE.md boundary table — real, not vague

```markdown
| Port | Adapter(s) | Notes |
| ---- | ---------- | ----- |
| `TaskQueue` | `InMemoryQueue`, `RedisQueue`, `PostgresQueue` (in progress) | domain/consumer code never imports a backend directly |
| `Clock` | `SystemClock`, `FakeClock` (tests) | kept injectable for deterministic lease-timeout tests |
```

Not this:
```markdown
| Port | Adapter(s) | Notes |
| ---- | ---------- | ----- |
| (fill in) | (fill in) | |
```
If there's nothing real to put in the table yet (true greenfield), leave the
scaffold's HTML comment as-is rather than inventing rows.

## RELEASE_NOTES.md entry — reasoning included, limitations stated plainly

```markdown
## PR #18 — Close the two honestly-disclosed gaps from prior backlog work
**2026-07-20** · [#18](...)

- **Fixed:** approving and resuming a `merge_pr`/`deploy` escalation no longer
  leaves that PR's release record stale at `AwaitingApproval`.
- **Known limitation, tracked honestly rather than left ambiguous:** a real
  live-org verification is still outstanding.
```

The bolded category tag is inline in the bullet, not a subheader. Limitations get
stated as their own bullet, not folded into a vague "misc fixes" line.

## PR description — reasoning, not just a diff summary

```markdown
## Bug
Fixes #142

When `lease_renew` fails, the task's visibility timeout wasn't reset — so it could
become visible to other consumers mid-processing and get picked up twice.

## Root cause
`lease_renew` updated local expiry tracking *before* confirming the write succeeded.
```

Root cause is *why*, not a restatement of the symptom. If the PR template's
checklist items are being filled for real (not left as a scaffold), check only the
ones actually true — an unchecked box is honest signal, not a gap to hide.

## README license line — greenfield default vs. real repo

Greenfield: `Internal — not for external distribution`

Once the repo has a real license decision, replace that line — don't leave the
greenfield default in a repo that's since decided otherwise.
