---
name: csv-cleaner
description: >-
  Cleans messy CSV exports. Use when the user hands over a CSV and asks to clean,
  normalize or dedupe it.
metadata:
  version: "1.2.0"
---
# csv-cleaner

1. Run `python3 tools/sniff.py <file>` to detect the delimiter and encoding.
2. Normalize headers to snake_case.
3. Parse dates into ISO 8601.
4. Remove duplicate rows.
5. Write `<name>.clean.csv` next to the input and report row counts before and after.
