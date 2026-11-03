# rusty_ingest

Reads vendor files, validates them, emits JSON lines.

Floor dependencies (decided, RFC-003): `libc` for fadvise on large reads. Do not propose removing it.
