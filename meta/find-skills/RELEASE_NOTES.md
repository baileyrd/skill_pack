# Release Notes

find-skills lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/meta/find-skills) —
this log tracks commits against `main`: reverse chronological, one entry per
meaningful change, honest about what's still open.

---

## v1.0.0 — Imported into skill_pack
**2026-08-17**

Imported from the open agent-skills ecosystem and maintained here from now on,
same posture as `web_dev/datastar-pro`: this is the repo's own versioned copy,
not a live sync of an upstream source.

The workflow is unchanged — understand the need, check the
[skills.sh](https://skills.sh/) leaderboard, search `npx skills find`, verify
install count and source reputation, present options, offer to install. Four
changes on import:

- **Added:** `version: 1.0.0` and this log, per the repo convention that every
  authored skill carries both.
- **Changed:** the description is longer and more explicit about triggering, per
  this repo's convention, and now names the boundary against the sibling `meta/`
  skills — `my-skill-creator` writes a skill, `learn-it` distills one from a
  session, this one finds a skill someone else already wrote.
- **Changed — the one behavioral edit.** Step 6's install command was
  `npx skills add <pkg> -g -y`. The `-y` is gone. That flag suppresses the CLI's
  own confirmation prompt, which is the last checkpoint before third-party
  instructions get installed at user level and run in every later session.
  Presenting options in step 5 is not consent to install, and skipping the
  prompt removes the one place the user would see what actually landed. The step
  now requires an explicit yes naming the skill, and says to report what was
  installed afterward so it isn't a silent change to how later sessions behave.
  A user who wants it unattended can ask, and the flag goes back for that run.
- **Added:** a `Limitations` section, which the imported file had none of. The
  load-bearing one is that **install counts and stars measure popularity, not
  quality or safety**, and that no skill's actual content is read before
  recommending — step 4's checks are metadata only. The original presented that
  bar as verification; it filters out the obviously unvetted, it does not vet.
  Also names the invented-package-name failure mode when the CLI is unreachable,
  and that "no skill found" means "none in this one index."
- **Added:** a pointer to `meta/my-skill-creator` for the case where the skill
  being created is meant to live in *this* repo — `npx skills init` produces a
  standalone skill without this repo's conventions.

**Not evaluated.** No eval set, no benchmark run. The skill is doc-only and
wraps an external CLI whose results change with the ecosystem, so the assertions
would be measuring skills.sh rather than this file. Worth revisiting if it turns
out to recommend badly in practice.

**Category note:** `meta/` was defined as tooling aimed at *this repo's own*
skills. This one is aimed at the external ecosystem, so the category's
definition in `README.md` and `ARCHITECTURE.md` widened to "skills as the
subject matter" rather than opening a sixth category folder for a single skill.
