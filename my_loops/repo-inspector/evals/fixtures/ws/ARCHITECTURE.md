# Workspace architecture

- `libc` is a deliberate floor dependency (ADR-002); don't propose replacing it.
- `to_hex` exists in both net_http and api_client on purpose: a prior dedupe pass
  (ADR-004, 2026-09) decided a shared crate for a one-line helper costs more than
  the copy. Keep both.
