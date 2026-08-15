# ADR-0003: `.gitattributes` is repo-config's business, `.gitignore` is not

Status: Accepted
Date: 2026-08-15

## Context

`repo-config`'s stated Limitations drew its boundary by *category*: it
applies governance files and "deliberately doesn't touch LICENSE,
`.gitignore`, or anything aimed at going public." Repo-level git
configuration was excluded wholesale, without the exclusion being argued —
`.gitignore` and `.gitattributes` sat on the same side of the line because
they're both dotfiles that configure git.

The forcing function was `repo-config`'s own `audit.sh` failing to run. The
copy synced to `~/.claude/skills/synced/repo-config/` arrived with CRLF line
endings and died on its own shebang:

```
audit.sh: line 5: $'\r': command not found
audit.sh: line 6: set: pipefail: invalid option name
```

The repo's index was clean LF the whole time — `git add --renormalize .`
produced zero changes. The corruption happened *after* checkout, on the path
from a Windows working tree to a Linux consumer. A `.gitattributes` with
`eol=lf` prevents exactly this, and every repo `repo-config` touches is
authored on Windows and consumed by Linux/macOS harnesses. So the file that
would have prevented a real failure was excluded by a boundary drawn on
category rather than on consequence.

## Decision

Redraw the boundary by **what kind of file it is**, not by where it lives:

- **`.gitattributes` is in scope.** There is one correct answer for every
  repo in this ecosystem, it needs no per-project judgment, and getting it
  wrong breaks scripts *at a distance* — in a copy nobody is looking at,
  with an error message that names a line number rather than the cause.
- **`.gitignore` stays out.** What's ignorable is genuinely per-project, and
  a wrong guess fails *silently* in the worst direction: a real file that
  should have been committed simply isn't, and nobody finds out until
  something is missing somewhere else.

The distinguishing question is not "is this git config?" but: **does this
file have the same correct content everywhere, and does getting it wrong
fail loudly or silently?** Same-everywhere and loud is a good candidate for
a template. Per-project or silent is not.

The template carries one thing this repo's own `.gitattributes` didn't need:
`.bat`, `.cmd` and `.ps1` pinned to `eol=crlf`, because Windows-native
scripts genuinely want CRLF and a blanket LF rule would break them on the
way to fixing the shell scripts.

`audit.sh` gains it as an 11th item — and, uniquely among the eleven, a
*correctness* check rather than a presence check. A repo can carry a
`.gitattributes` that only marks binaries and still hand out CRLF shell
scripts, so the audit greps for `eol=lf` and warns when a present file
doesn't enforce it. For this one item, presence is the wrong question.

## Alternatives considered

**Leave the boundary alone; fix only this repo.** Cheapest, and it was the
state after the first fix. It lost because the failure isn't specific to
`skill_pack` — every repo `repo-config` touches has the same
Windows-authored/Linux-consumed shape, so leaving the template out means each
one rediscovers this the same way: a script that won't run, in a copy nobody
is looking at.

**Bring `.gitignore` in too, for consistency.** Rejected on the silent-
failure asymmetry above. Consistency between two files that fail in opposite
ways isn't a virtue; a `.gitignore` guess that's wrong stops a real file from
being committed and produces no error at all.

**Solve it with a lint check instead of a template.** A check tells you the
file is missing; the template means it isn't. Both were done — the check
exists in `audit.sh` — but a check alone leaves every new repo starting from
broken and waiting to be told.

**Treat presence as sufficient, like the other ten items.** Rejected because
a binaries-only `.gitattributes` scores present while leaving the exact
problem in place. This is the same presence-vs-currency gap `audit.sh`
already flags for `RELEASE_NOTES.md`, applied where a wrong file is worse
than a missing one.

## Consequences

- **`audit.sh`'s denominator moves 10 → 11.** A previously-perfect repo now
  scores 10/11 until the file is applied. That's the intended signal, not a
  regression, but it will surface on every repo the skill has already been
  run against.
- **The exclusion list now needs a reason per entry**, not a category. Any
  future proposal to add repo-level config to the template set has to answer
  the same-everywhere and loud-or-silent questions rather than pointing at
  precedent.
- **It doesn't fix what's already broken.** A checkout that already has CRLF
  files needs one `git add --renormalize .`, and a copy already synced
  elsewhere is out of reach entirely — the `audit.sh` that prompted this
  stays broken until re-synced. The template prevents the next occurrence; it
  doesn't repair the current one.
- **`.gitattributes` cannot fix the executable bit**, which is the same
  Windows-authored/Linux-consumed problem in its other half. Git has no
  attribute for permissions. That half is handled by
  `scripts/restore_exec_bits.py` and the `exec-bits` check in
  [ADR-0002](./0002-repo-checks-require-a-real-failure.md); the two are
  siblings, and neither substitutes for the other.
