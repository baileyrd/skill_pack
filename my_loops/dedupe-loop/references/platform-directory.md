# Platform repo directory (baileyrd/* + Rusty-Mill/*)

Repos worth checking for an existing implementation before hand-rolling.
Refreshed 2026-08-15 against the live namespaces.

## Read this before using the table

**Almost everything lives under `baileyrd`, not `Rusty-Mill`.** The previous
version of this file listed ~25 repos as `Rusty-Mill` (rustils, rusty_json,
rusty_http, rusty_libc, rusty_tokio, rusty_wire, …). None of them are. Building
a clone URL from that column produced 404s for every one. Only **four** repos
are actually in the `Rusty-Mill` org, listed below. If migration to the org is
still intended, it hasn't happened yet — assume `baileyrd` unless this file
says otherwise.

**Three repos in the old list don't exist under those names:** `rush`,
`rusty_compactor` (it's `rusty_token_compactor`), and `rusty_tail` (it's
`rusty_tailscale`).

**Purpose column:** entries marked † are inferred from the repo name and have
**not** been confirmed by reading the source. The `rusty_<thing>` ≈
`<external crate>` pattern is a first-pass filter, not proof — a name match
still needs a source read before it counts as `covered`. Unmarked entries were
confirmed by reading the repo.

## Rusty-Mill org (all four)

| Repo | Purpose |
| --- | --- |
| rusty_foundation_akb | Architecture knowledge base — docs only, never a reuse candidate |
| rusty_knowledge | Knowledge base † |
| rusty_owl | Private; purpose unconfirmed † |
| .github | Org-level community health files |

## baileyrd — platform / stdlib layer

| Repo | Purpose |
| --- | --- |
| rustils | OS abstraction / platform-core (`platform`, `platform-linux`, `platform-bsd`, `platform-windows`, `platform-mock`, `coreutils`, `winargv`). The designated floor per ADR-011 |
| rustils_async | Async layer above rustils: `reactor-core` (runtime-agnostic, no I/O), `platform-async`, `platform-async-linux` (pidfd + epoll), `threading`, `coreutils-async` |
| rusty_std | std reimplementation; depends on rusty_libc + rusty_win32 |
| rusty_libc | libc reimplementation, tracked for parity against the `libc` crate |
| rusty_win32 | Win32 API bindings |
| rusty_tokio | Async runtime (tokio-adjacent) |
| rusty_sync | `no_std` + alloc spinlock, spinlock-protected MPMC channel, ring buffer. **Not** a work-stealing deque |
| rusty_parking_lot | Private; `parking_lot`-adjacent locks † |
| rusty_async | **Empty repository** — nothing in it |
| rusty_simd | SIMD † |
| rusty_boot | Boot/init † |

## baileyrd — data / encoding

| Repo | Purpose |
| --- | --- |
| rusty_wire | Zero-dependency endian-explicit byte cursor Reader/Writer. **Not** the `bytes` `Buf`/`BufMut` trait ecosystem |
| rusty_json | JSON parsing/serialization † |
| rusty_serde | serde-adjacent † |
| rusty_codec | Codec † |
| rusty_compress | Compression † |
| rusty_uuid | UUID † |
| rusty_sha256 | SHA-256 † (private) |
| rusty_crypto_key | Key handling † |
| rusty_ansder | ASN.1 DER † |
| rusty_regx | Regex engine † |
| rusty_text | Text processing † |
| rusty_lines | Line-oriented text processing † |
| rusty_diff | Diffing † |
| rusty_jinja | Jinja-style templating † |
| rusty_font | Font handling † |

## baileyrd — network / protocol

| Repo | Purpose |
| --- | --- |
| rusty_http | HTTP client/server † |
| rusty_h2 | HTTP/2 † |
| rusty_request | HTTP request client (Requests-adjacent) † |
| rusty_tls | TLS † |
| rusty_url | URL parsing † |
| rusty_croc | Peer-to-peer file transfer (croc-like) † |
| rusty_rdp | RDP client † |
| rusty_tailscale | Tailscale implementation † (private) — the dedicated-repo precedent for an XL hand-roll |
| rusty_wiremock | HTTP mocking † |
| rusty_oauth | OAuth † (private) |
| rusty_stream | Streaming † — consumes rusty_tokio's io-uring surface |

## baileyrd — storage / data stores

| Repo | Purpose |
| --- | --- |
| rusty_db | Database abstraction (SQLAlchemy-like) † |
| rusty_sqlite | SQLite † |
| rusty_rusqlite | rusqlite-adjacent † (private) |
| rusty_dbs | † (private) |
| rusty_search | Search engine abstraction † |
| rusty_config | Configuration † |
| rusty_dirs | Directory/path conventions † (private) |
| rusty_git | Git † |
| rusty_inventrory | Inventory † (name is misspelled in the repo itself) |

## baileyrd — terminal / UI / graphics

| Repo | Purpose |
| --- | --- |
| rusty_term | Terminal emulation/handling † |
| rusty_termius | Terminal † (private) |
| rusty_naner | Cmder-adjacent terminal † |
| rusty_ansi | ANSI escape handling † |
| rusty_gui | GUI † |
| rusty_gpu | GPU † |
| rusty_vulkan | Vulkan † |
| rusty_nexus | † |

## baileyrd — AI / agent tooling

| Repo | Purpose |
| --- | --- |
| rusty_prime_agent | Rust rewrite of Prime Agent's daemon/worker/session core |
| rusty_provider | LLM provider/service abstraction † |
| rusty_llama | Local LLM inference (llama.cpp-style) † |
| rusty_llama-fs | LLM filesystem † |
| rusty_embedder | Embeddings † |
| rusty_whisper | Speech-to-text † |
| rusty_voice | Voice † |
| rusty_audio | Audio † |
| rusty_mcp | Model Context Protocol † |
| rusty_acp | Agent Client Protocol † |
| rusty_a2a | Agent-to-agent † |
| rusty_adk | Agent development kit † |
| rusty_agent_gateway | Agent gateway † |
| rusty_remind_me | Reminder/memory service (has a live MCP server) |
| rusty_token_compactor | Token compactor † |
| rusty_SkillOpt | Skill optimization † |
| rusty_knowledge | see Rusty-Mill above |

## baileyrd — tooling / meta

| Repo | Purpose |
| --- | --- |
| rusty_lsp | Language Server Protocol † |
| rusty_test | Test tooling † |
| rusty_err / rusty_error | Error handling † (two repos; `rusty_error` is private — relationship unconfirmed) |
| rusty_time / rusty_chrono | Time/date † (two repos; `rusty_chrono` is private) |
| rusty_repo_checker | Repo checking † (private) |
| rusty_repo_wise | Repo analysis † |
| rusty_headroom | † |
| Rusty_OMP | † (private) |
| Rusty_Key | † (private) |
| Atlas_Engineering_Standards_Library | Standards library — docs only, never a reuse candidate |

## Known transitive-dependency note

`rustils`' `platform` crate depends on `thiserror`, which pulls `thiserror-impl`
→ `syn` + `quote` + `proc-macro2` + `unicode-ident` into **every** consumer of
the platform layer. Worth knowing before classifying any of those four as a
hand-roll candidate in a downstream repo: removing them there does not remove
them from the build. See rusty_tokio's `dependency-audit.md` for the worked
example, where this invalidated an entire audit row.

## Resolving a bare repo name

Build the slug as `baileyrd/<repo>` unless the repo is one of the four
Rusty-Mill entries above. If a clone 404s, try the other namespace before
concluding the repo doesn't exist — and update this file when you find one that
has moved.
