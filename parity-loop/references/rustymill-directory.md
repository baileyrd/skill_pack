# RustyMill org directory

A snapshot of the RustyMill GitHub org's repos and their purpose, as of when
this file was written. Treat it as a cache to confirm against `gh repo list
RustyMill`, not gospel — the org grows, and this file drifts. Refresh it
(or at least spot-check the repos relevant to the current run) rather than
assuming it's still complete.

| Repo | Purpose |
| --- | --- |
| rush | Native shell |
| rustils | OS abstraction / platform-core layer |
| rusty_ansder | ANS DER |
| rusty_compactor | Token compactor |
| rusty_croc | Peer-to-peer file transfer (croc-like) |
| rusty_db | Database abstraction layer, SQLAlchemy-like |
| rusty_h2 | HTTP/2 protocol implementation |
| rusty_http | HTTP client/server library |
| rusty_json | JSON parsing/serialization |
| rusty_libc | libc reimplementation, tracked for parity against the `libc` crate |
| rusty_lines | Line-oriented text processing utility |
| rusty_llama | Llama.cpp-style local LLM inference |
| rusty_lsp | Language Server Protocol implementation |
| rusty_naner | Cmder-adjacent terminal implementation |
| rusty_provider | LLM provider/service abstraction layer |
| rusty_rdp | RDP (Remote Desktop Protocol) client/implementation |
| rusty_regx | Regular expression engine |
| rusty_request | HTTP request client (Python Requests-adjacent) |
| rusty_search | Search engine abstraction layer |
| rusty_tail | Rust-based Tailscale implementation |
| rusty_term | Terminal emulation/handling library |
| rusty_tls | TLS implementation |
| rusty_tokio | Async runtime tooling (tokio-adjacent) |
| rusty_url | URL parsing library |
| rusty_whisper | Speech-to-text (Whisper-based) |
| rusty_win32 | Windows API (Win32) bindings |
| rusty_wire | Wire protocol / binary serialization |
| SHH | SSH-related tool |

Many of these are themselves purpose-built to stand in for a specific
external crate (`rusty_json` ~ `serde_json`, `rusty_regx` ~ `regex`,
`rusty_url` ~ `url`, `rusty_tls` ~ `rustls`, `rusty_http`/`rusty_request` ~
`reqwest`/`hyper`, `rusty_tokio` ~ `tokio`, `rusty_wire` ~ things like
`bincode`/`prost`). That naming pattern is a decent first-pass heuristic for
which repo to check first, but confirm by reading the actual source — a
name match isn't the same as coverage.
