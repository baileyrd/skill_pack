# Release Notes

project-expert lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/dev_practices/project-expert).

---

## v1.0.0 — Initial release
**2026-11-10**

- **Added:** stands up an in-repo project expert with or without an existing
  handoff pack, generalized from a one-off "apply project-handoff to a
  monorepo project" prompt. Intake table (scope globs, existing decision log,
  chat link, tags, reviewer), a pack/no-pack fork, an ordered source sweep that
  reports unreadable sources instead of guessing, a pointer-style DECISIONS for
  projects with an existing log, branch-from-unmerged-docs-branch delivery, and
  six acceptance checks. Builds on project-handoff v1.3.0 templates rather than
  duplicating them.

- **Fixed (found by a blind dry run on baileyrd/portfolio_intelligence, where an
  open PR already held a pack):** the pack check runs first and also looks at
  open PRs and branches, judged by changed files; `remind_me_search` is given a
  query (the tool rejects `include_raw` without one); agent-written docs and
  reviews under the user's login are `[default]`, not `[stated]`; QA seeding
  overrides harvest's empty QA; repo with only AGENTS.md gets a CLAUDE.md plus a
  pointer; slug spelling and board-key aliases; acceptance replaces the
  post-merge smoke test; reversal check uses a `[stated]` prohibition.
