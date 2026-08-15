# Platform repo directory (baileyrd/rusty_* + Rusty-Mill/*)

A snapshot of repos worth checking for an existing implementation before
hand-rolling a gap fix, spanning **both** namespaces — the personal
`baileyrd/rusty_*` repos and the `Rusty-Mill/*` org. Org migration from the
personal namespace to `Rusty-Mill` isn't complete, so a given repo may live
in either place; treat this as one merged list, not two to check
separately. Confirm against `gh repo list Rusty-Mill` and a check of the
`baileyrd` namespace since both grow and repos move between them over
time — this file is a cache, not gospel.

| Repo | Namespace | Purpose |
| --- | --- | --- |
| rush | Rusty-Mill | Native shell |
| rustils | Rusty-Mill | OS abstraction / platform-core layer (`rust-platform-core`) |
| rusty_ansder | Rusty-Mill | ANS DER |
| rusty_compactor | Rusty-Mill | Token compactor |
| rusty_croc | Rusty-Mill | Peer-to-peer file transfer (croc-like) |
| rusty_db | Rusty-Mill | Database abstraction layer, SQLAlchemy-like |
| rusty_h2 | Rusty-Mill | HTTP/2 protocol implementation |
| rusty_http | Rusty-Mill | HTTP client/server library |
| rusty_json | Rusty-Mill | JSON parsing/serialization |
| rusty_libc | Rusty-Mill | libc reimplementation, tracked for parity against the `libc` crate |
| rusty_lines | Rusty-Mill | Line-oriented text processing utility |
| rusty_llama | Rusty-Mill | Llama.cpp-style local LLM inference |
| rusty_lsp | Rusty-Mill | Language Server Protocol implementation |
| rusty_naner | Rusty-Mill | Cmder-adjacent terminal implementation |
| rusty_provider | Rusty-Mill | LLM provider/service abstraction layer |
| rusty_rdp | Rusty-Mill | RDP (Remote Desktop Protocol) client/implementation |
| rusty_regx | Rusty-Mill | Regular expression engine |
| rusty_request | Rusty-Mill | HTTP request client (Python Requests-adjacent) |
| rusty_search | Rusty-Mill | Search engine abstraction layer |
| rusty_tail | Rusty-Mill | Rust-based Tailscale implementation |
| rusty_term | Rusty-Mill | Terminal emulation/handling library |
| rusty_tls | Rusty-Mill | TLS implementation |
| rusty_tokio | Rusty-Mill | Async runtime tooling (tokio-adjacent) |
| rusty_url | Rusty-Mill | URL parsing library |
| rusty_whisper | Rusty-Mill | Speech-to-text (Whisper-based) |
| rusty_win32 | Rusty-Mill | Windows API (Win32) bindings |
| rusty_wire | Rusty-Mill | Wire protocol / binary serialization |
| SHH | Rusty-Mill | SSH-related tool |
| rusty_foundation_akb | Rusty-Mill | Architecture knowledge base — docs only, not a code source for reuse |
| Atlas_Engineering_Standards_Library | baileyrd | Standards library — docs only, not a code source for reuse |
| rusty_prime_agent | baileyrd | Rust rewrite of Prime Agent's daemon/worker/session core |

The two standards/AKB repos are listed for completeness but are never reuse
candidates — see `references/development-standards.md` for how they're
actually used.

Many of the `rusty_*` repos are purpose-built stand-ins for a specific
external crate (`rusty_json` ~ `serde_json`, `rusty_regx` ~ `regex`,
`rusty_url` ~ `url`, `rusty_tls` ~ `rustls`, `rusty_http`/`rusty_request` ~
`reqwest`/`hyper`, `rusty_tokio` ~ `tokio`, `rusty_wire` ~ things like
`bincode`/`prost`). That naming pattern is a decent first-pass heuristic,
not proof; confirm by reading the actual source — a name match isn't the
same as coverage.

## Resolving a bare repo name

`scripts/index_capabilities.sh` takes a **local repo path**, not a repo
name — dedupe-loop has no clone step of its own, unlike the sibling skills
whose `scan_platform_repos.sh` will fetch a repo it doesn't have. So a repo
in `PLATFORM_REPOS` that isn't checked out locally has to be cloned before
step 1 can index it:

```bash
gh repo clone <namespace>/<repo> /path/to/scratch/<repo> -- --depth 1
```

Use this table's **Namespace** column to build that slug — don't assume
everything is still under the personal namespace or that migration to
`Rusty-Mill` is finished for a given repo; check this table first, then fall
back to trying both namespaces if a repo isn't listed here yet.

A shallow clone is enough: `index_capabilities.sh` reads the working tree
only and never looks at history.
