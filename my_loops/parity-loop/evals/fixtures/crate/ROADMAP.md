# Roadmap

Parity target: Python 3.13 `posixpath`, string functions only.

| Function | Status |
|---|---|
| basename, dirname, join | done (0.3.0) |
| split, splitext | planned 0.4 |
| normpath | planned 0.4 |
| isabs, commonpath | planned 0.5 |
| realpath, abspath | needs filesystem/cwd access; this crate is pure-string today |

Out of scope: `ntpath` (Windows paths), `expandvars`, `expanduser`.
