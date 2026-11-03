# tidy

`tidy` removes stale files from a directory.

## Install

    pip install tidy-cli

## Usage

    tidy PATH --older-than DAYS [--dry-run] [--recursive]

`--recursive` descends into subdirectories. Paths listed in `.tidyignore` are
never deleted. `tidy` refuses to run on `/` or your home directory.

See [the design notes](docs/design.md) and [CONTRIBUTING](CONTRIBUTING.md).

Requires Python 3.9+.
