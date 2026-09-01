# Release Notes

implementation-merge lives at
[github.com/baileyrd/skill_pack](https://github.com/baileyrd/skill_pack/tree/main/my_loops/implementation-merge),
same convention as
[repo-config's RELEASE_NOTES.md](../repo-config/RELEASE_NOTES.md):
reverse chronological, one entry per meaningful change, honest about what's
still open.

---

## v1.1.0 — skill-retro findings from the first real run (F1–F4)
**2026-09-01**

Applied all four findings from a `skill-retro` pass grounded in the first
real end-to-end run of this skill (`rusty_oauth`'s/`rusty_rdp`'s `BigUint`
merge, 13/13 tests passing).

- **F1 (fixed a factual error):** the worked example throughout `SKILL.md`
  (description, intro, step 2) claimed `rusty_oauth`/`rusty_rdp` share an
  "HMAC-SHA256" case — wrong, inherited uncorrected from `repo-inspector`'s
  own report. Re-reading the actual source for the real run found
  `rusty_rdp`'s `hmac.rs` has no `hmac_sha256` at all (only
  `hmac_md5`/`hmac_sha1`, for NTLM/Kerberos). Replaced the worked example
  throughout with `BigUint` — the case actually run and verified — and
  noted the correction as an instance of F2's own point.
- **F2 (new guidance, step 0):** a `dedupe-loop`/`repo-inspector` cluster
  row can bundle more than one distinct capability under one row — the
  real row this skill's worked example came from bundled HMAC, RSA, and
  `BigUint` together, only one of which turned out mergeable-complementary
  on a close read. Step 0 now says to check by reading, not row count, and
  run this skill once per genuinely separate capability.
- **F3 (new guardrail, step 4 split into 4a/4b):** the first real run
  skipped the mechanical coverage re-run ("confirm every kept/merged item
  is actually present in the proposal") — the stated enforcement mechanism
  for this skill's one core rule — relying only on the test-suite check.
  It turned out clean when re-run for the retro, but that was luck, not
  something the test suite established. Step 4 is now two explicit,
  ordered sub-steps: 4a (the mechanical check, required first) and 4b
  (test-suite verification) — both required for step 5, not one required
  and one bundled-in-as-an-aside.
- **F4 (reframed, step 3):** "using whichever candidate's structure is the
  more solid base" undersold what actually worked best in the real run —
  per-item synthesis with no single base file. Step 3 now says so
  explicitly, while still allowing a single candidate as the base when
  that's genuinely the right call.
- Not applied: none — all four findings from the retro were approved.

## v1.0.1 — Match `pub(crate)`/`pub(super)`, not just bare `pub`
**2026-09-01**

- **Fixed:** `extract_public_surface.sh`'s regex only matched bare `pub
  fn`/`pub struct`/etc., silently missing anything scoped `pub(crate)` or
  `pub(super)` — invisible to `coverage_matrix.py` and therefore to the
  coverage table entirely. Found running this skill for real for the
  first time: `rusty_oauth`'s `BigUint` has `add`/`sub`/`mul` as
  `pub(crate)` (used internally by its RSA/ECC modules), and none of the
  three showed up in the comparison until this fix — a real merge
  candidate's shared internals are routinely `pub(crate)`, not just
  fully-`pub`, so this wasn't an edge case.
- Caught only because step 1 (read the actual source) is a hard
  requirement independent of the tooling — the merge proposal that
  resulted was correct despite the bug, but only because the instructions
  don't let a run trust the coverage matrix alone. The bug itself would
  have produced a silently incomplete coverage table for any cluster with
  crate-internal (not fully public) shared surface, which is common.
- **Added:** a Limitations note that even after this fix, fully **private**
  items (no `pub` qualifier at all) are correctly invisible to the
  tooling — a private helper being dropped or kept is still a real design
  choice worth writing up in `MERGE-PROPOSAL.md`, caught by step 1's
  manual read, never by the scripts.
- Grounded in the first real run of this skill: a genuine merge of
  `rusty_oauth`'s and `rusty_rdp`'s `BigUint` implementations, verified
  13/13 against both crates' own test suites (delivered directly, per
  step 5 — not committed anywhere, since v1 never writes into a
  candidate's real path).

## v1.0.0 — Initial release
**2026-09-01**

- **Added:** first cut of `implementation-merge`, a standalone skill that
  picks up where `dedupe-loop`'s step 4.1 and `repo-inspector`'s
  `convergent-but-diverged` classification stop — both correctly refuse to
  silently pick a winner between two implementations, but neither actually
  attempts a merge. This skill does: given 2+ already-identified
  candidates, it classifies mergeability fresh (mergeable-complementary /
  mergeable-conflicting / not-mergeable), and for mergeable clusters
  produces a `MERGE-PROPOSAL.md` plus a proposed merged source at a scratch
  location — dry-run only, same posture as `repo-inspector` (no code lands
  in a candidate's real path, no PR, no merge).
- **New scripts:** `extract_public_surface.sh` (reuses
  `repo-inspector`'s `index_workspace_capabilities.sh` extraction logic,
  scoped to N explicitly-named candidates instead of a whole workspace) and
  `coverage_matrix.py` (reuses `find_clusters.py`'s normalization, but
  deliberately does **not** filter to multi-candidate items — a
  single-candidate row is exactly what the coverage table and "never
  silently drop" rule need).
- **Verified against a real cluster while building this skill**: both
  scripts were run against `rusty_oauth`'s and `rusty_rdp`'s crypto
  primitives in `Rusty-Mill/rusty_mill` — the same near-duplicate HMAC-
  SHA256/`RsaPublicKey`/`BigUint` cluster `repo-inspector`'s own first real
  run flagged. The coverage matrix correctly surfaced the full picture:
  not just the three items already known, but also an independent
  `SHA-256` reimplementation in both crates (missed in the earlier,
  hand-read pass), `rusty_oauth`'s `constant_time_eq` (present in
  `rusty_oauth` only — a real, security-relevant item a careless merge
  could silently drop), and `rusty_rdp`'s NTLM/CredSSP-specific hash
  variants (`hmac_md5`/`hmac_sha1`, correctly out of scope for a general
  HMAC-SHA256 merge, not items to fold in just because they showed up in
  the same file). Confirms the coverage-matrix approach surfaces real,
  actionable detail beyond what a first manual read caught — this skill's
  core value case, not just a smoke test.
