# Migrating notify to Rust

Agreed with the team on 2026-10-20:

- Target crate: `notify-rs`, single binary, no async runtime.
- `--legacy-csv` is OUT OF SCOPE: the last caller (the billing cron) was removed in
  September. (decided by Nano)
- Everything else keeps working exactly as today, exit codes included.
