# Auditing the context layer

The context layer is the folder of notes Claude reads to know the business: `context/`, a wiki, a
vault, a "second brain". It can hold hundreds of files. Reading them all is slow, costly and still
misses things, so the audit runs in four layers and only the last one needs your judgement.

## 1. Coverage (the script)

`context_inventory.json` has one row per file in every context folder: size, last change, how
often Claude read it in the window (from session history), how many files link to it, whether the
manifest routes to it, and whether it sits in a raw or retired folder. The report's first context
line states coverage as "N of N files". If the owner keeps notes somewhere the script didn't find,
re-run with `--context-dir <folder>`.

## 2. Folders first

Rule by folder before file. The report's folder table gives each folder a verdict:

| Verdict | Means | Usual ruling |
|---|---|---|
| live | read 3+ times in the window, or changed in the last 14 days | keep; check its orphans |
| reference | linked or routed, but not read lately | keep if the facts are still true |
| cold | not read, not linked, not routed, unchanged for 60+ days | archive the folder |
| raw | evidence, sources, research, examples | keep out of routing; check size only |
| retired | `_retired` / `archive` inside the layer | move to the workspace archive |

Present cold folders as one decision each, not a file list.

## 3. Signals inside live folders

Raise file-level items only where a signal points:

- **found by search**: Claude read it but nothing links or routes to it. Link it.
- **read but unrouted**: read 3+ times, no manifest route. Route it.
- **routed but never read**: the manifest points at it and nothing read it. The skill that should
  read it may have changed, or the fact is retired.
- **hot and heavy**: read often and large. Put a short summary first or split it.
- **stacked versions**: the same headings repeat inside one file. Keep the current version.
- **broken links and dead routes**, **identical files**, **folders with no index**.

## 4. Facts that must agree (you)

`facts.jsonl` holds fact lines (prices, offers, audience, brand, models and tools, anything marked
default, current, retired or replaced) from the files Claude actually reads, plus CLAUDE.md,
grouped by topic. For each topic, compare the lines and flag every pair of files that disagree.
Quote both lines with their files and last-change dates, and say which looks current. Then check
the memory index for the same topics. Contradictions are the costliest finding in a context layer:
Claude follows whichever file it read last.

Don't open files to judge them unless a signal or a contradiction points there. When you do, read
the top of the file first.

## What to leave alone

- Raw material (evidence, transcripts, research) is meant to sit unlinked.
- A wiki or knowledge base with its own maintenance skill keeps its own fact checks. Report
  structure here and leave fact-checking to that skill.
- Brand assets that renderers read (logos, fonts, tokens) belong in the layer even though they are
  not text.
