# ADR-0002: A repo check is added only for a failure this repo has actually had

Status: Accepted
Date: 2026-08-15

## Context

`repo-config`, this repo's own governance skill, has a standing rule: no
language manifest, no CI workflow, because *an always-red workflow is worse
than none*. `skill_pack` has no manifest — it is a tree of markdown and
one-shot Python tooling — so for its whole life it had no CI, and
`CONTRIBUTING.md` nevertheless said "CI must be green before merge." A
`docs-loop` run classified that as **aspirational**: a claim that was never
true rather than one that rotted.

The forcing function was a single day's work that surfaced four defects
nobody had noticed, each found by hand and each costing a PR:

- 18 tracked scripts committed `100644` despite starting with `#!`, shipping
  non-executable for months (PR #22).
- A synced copy of `repo-config`'s own `audit.sh` arriving with CRLF and
  dying on its own shebang (PR #20).
- A reference to a script a skill doesn't have, and a table-of-contents
  anchor pointing at no heading (issues #16, #17).
- Six skills' dependency declarations wrong in both directions — five
  understating, one claiming a `ripgrep` requirement no script had (PR #25).

Every one of those is mechanically checkable. Every one was found by a human
reading carefully, which does not scale and did not happen for months.

## Decision

Add CI, as a deliberate exception to `repo-config`'s no-manifest rule, under
a constraint that makes the exception safe:

**A check earns its place by naming the commit it would have failed.**

Not by being good practice, not by being cheap, not by being what other
repos do. `scripts/check_repo.py`'s docstring names the failure behind each
of its five checks, and that docstring is the admission criterion for a
sixth.

Three corollaries, each load-bearing:

1. **A check must be demonstrated failing before it ships.** Injecting the
   fault is part of adding the check. This is not ceremony: two of the five
   silently passed on their first fault injection — one because
   `.gitattributes` had already fixed the problem upstream, one because the
   injected `raise` was unreachable code after the script's own `SystemExit`.
   A check that cannot be shown to fail is not a check.
2. **A check that cannot be green on day one gets a baseline, not a
   waiver.** `doc-refs` would have been red immediately from a documented,
   structural false-positive class (most docs here describe *other* repos).
   The baseline (`docs-refs-baseline.tsv`) accepts named rows with written
   reasons and fails on new breakage only. A permanently-red check is
   indistinguishable from no check within a week.
3. **Lint is not tests, and must not be described as tests.** These five
   checks verify repo structure, not behavior. `CONTRIBUTING.md` still
   requires tests for non-trivial logic and there is still no harness; that
   claim stays flagged as aspirational rather than being quietly satisfied by
   a green badge from a different kind of check.

## Alternatives considered

**Keep no CI, and delete the claim from `CONTRIBUTING.md`.** Honest, cheap,
and was a real option — `docs-loop` offered it as the alternative fix. It
lost because the four defects above are exactly the class a machine catches
for free and a human catches only by luck. Deleting the claim would have made
the docs accurate and the repo no better.

**Adopt a conventional lint stack** (a Python linter, a markdown linter, a
link checker off the shelf). Lost on the same reasoning that produced the
rule above: none of them would have caught the exec-bit or dependency-
declaration defects, which are specific to how *this* repo is built and
consumed, and each would have arrived with a backlog of style findings
unrelated to any failure anyone has had. Volume of findings is not value.

**Put the check logic in the workflow YAML.** Lost because it would only ever
run in CI. The logic lives in `scripts/check_repo.py` so a contributor can
run exactly what CI runs, before pushing; the workflow is four lines of
invocation.

**Wire `check_references.py --strict` in without a baseline.** Lost on
`repo-config`'s own always-red argument, which applies to a check that is red
for a legitimate reason just as much as to one that is broken.

## Consequences

- **A sixth check needs an incident, not an argument.** This deliberately
  forecloses adding checks because they seem sensible. If a defect class has
  never occurred here, the check for it does not go in — and when it does
  occur, the check becomes easy to justify.
- **The baseline is a maintenance surface.** Entries need written reasons,
  and stale ones are reported on every run. If it grows without reasons it
  stops being a record of judgment and becomes a mute button; that would be a
  reason to revisit this ADR.
- **CI reports but does not gate** until `repo checks` is set as a required
  status check in branch protection — a repo-admin action, not a commit.
  Until then `CONTRIBUTING.md`'s "CI must be green before merge" is a
  convention, and says so.
- **The tests question stays open**, visibly. Corollary 3 means this ADR
  does not close it, and the aspirational row for it remains in
  `docs-audit.md`.
- **`repo-config`'s no-manifest rule is now a rule with a documented
  exception**, which is a better state than an unexplained deviation. A repo
  with no manifest but real, repo-specific failure modes can point here.
