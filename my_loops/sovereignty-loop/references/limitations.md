# sovereignty-loop: limitations

Read this before treating a finished run as proof of completeness, or when
deciding whether this loop fits a job.

- Cross-repo search is keyword/grep-surfaced candidates plus judgment, not a
  guaranteed-complete scan — a platform repo solving this under different
  terminology can be missed. Worth a second pass by someone who knows the
  platform repos if the audit comes back suspiciously thin.
- The `rusty_<thing>` naming pattern is a decent first filter, not a
  guarantee — a name match still needs a source read before it counts as
  `covered`, and a genuine match can exist under an unrelated name.
  `references/platform-directory.md` is a snapshot and can drift from the
  live namespaces; confirm rather than assume it's complete.
- crates.io lookups need network reachability; air-gapped/SIPR runs fall
  back to local manifest/source data only, so "purpose" may be thinner than
  a connected run would produce.
- Direct dependencies only by default — the *audit* enumerates what the target
  itself names, not the full graph. Step 2.5 narrows this to the one question
  that changes a verdict ("does anything else reach this crate?"), but it
  doesn't make the audit a supply-chain review: it won't surface a risky
  transitive dependency nobody in the graph names directly, and it won't tell
  you what your dependencies' dependencies do. A real transitive-exposure pass
  is still a separate exercise.
- Step 2.5 answers *whether* a crate is reachable another way, not *how hard*
  that other path is to change. A row can be correctly reclassified `keep
  external` while the follow-up it points at turns out to be a fifteen-line
  fix in a sibling repo — that's a good outcome, but this skill won't size it
  for you. Chase the pointer.
- The S/M/L/XL hand-roll size is a routing gut-call (inline loop vs.
  dedicated-repo proposal), not a committed estimate — treat it as a
  starting point for scoping, not a promise.
- All three scripts require `gh` on `PATH` and authenticated. Step 0's
  preflight checks for it and routes to the GitHub MCP tools when it's
  missing, but that fallback is a documented substitution the run has to
  make deliberately — the scripts themselves have no MCP path.
- Doesn't decide *whether* sovereignty is worth the engineering cost for a
  given dependency — that's the judgment step 3 surfaces for the user, not
  something this skill resolves on its own.
