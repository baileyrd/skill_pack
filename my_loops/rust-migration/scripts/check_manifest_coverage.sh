#!/usr/bin/env bash
# check_manifest_coverage.sh <path-to-capability-manifest.md>
#
# The mechanical half of the boundary contract: parses capability-manifest.md
# (format: references/capability-manifest-format.md) and fails loudly if any
# row is not in a terminal state. A row passes only if:
#   - Status is DONE and the Evidence column is non-empty, or
#   - Status is OUT-OF-SCOPE and the Reason column is non-empty.
# A row with Status REQUIRED (the default — not yet migrated), an
# unrecognized status, or a terminal status missing its required column,
# fails the check and is printed by ID so it's easy to go fix.
#
# Run this as step 4's gate before ever reporting a migration finished.
# Exit 0 (all rows terminal) or 1 (at least one row still open), printing a
# summary either way.
#
# Requires: awk only. Locates the Status/Reason/Evidence/ID columns by
# header name (case-insensitive substring match), so it tolerates minor
# column reordering — but assumes a plain GitHub-flavored markdown pipe
# table with no escaped `\|` inside a cell.

set -euo pipefail

MANIFEST="${1:-}"
if [[ -z "$MANIFEST" || ! -f "$MANIFEST" ]]; then
  echo "Usage: check_manifest_coverage.sh <path-to-capability-manifest.md>" >&2
  exit 2
fi

awk -F'|' '
  function trim(s) {
    gsub(/^[ \t]+|[ \t]+$/, "", s)
    return s
  }
  function is_separator(line) {
    # a markdown header-separator row: only -, :, |, spaces
    t = line
    gsub(/[-: \t|]/, "", t)
    return (t == "")
  }
  BEGIN {
    header_seen = 0
    sep_seen = 0
    id_col = 0; status_col = 0; reason_col = 0; evidence_col = 0
    total = 0; done_n = 0; oos_n = 0; fail_n = 0
  }
  /^[ \t]*\|/ {
    if (!header_seen) {
      n = NF
      for (i = 1; i <= n; i++) {
        h = tolower(trim($i))
        if (h == "") continue
        if (h == "id")                id_col = i
        else if (h ~ /status/)        status_col = i
        else if (h ~ /reason/)        reason_col = i
        else if (h ~ /evidence/)      evidence_col = i
      }
      header_seen = 1
      next
    }
    if (!sep_seen) {
      sep_seen = 1
      if (is_separator($0)) next
      # no separator row present — fall through and treat this as data
    }
    if (status_col == 0) next  # malformed table, nothing to check on this line

    id = (id_col > 0) ? trim($id_col) : "(no id column)"
    status = toupper(trim($status_col))
    reason = (reason_col > 0) ? trim($reason_col) : ""
    evidence = (evidence_col > 0) ? trim($evidence_col) : ""

    if (id == "" && status == "") next  # blank row

    total++
    if (status == "DONE") {
      if (evidence == "") {
        fail_n++
        printf("FAIL  %-8s status=DONE but Evidence column is empty\n", id)
      } else {
        done_n++
      }
    } else if (status == "OUT-OF-SCOPE") {
      if (reason == "") {
        fail_n++
        printf("FAIL  %-8s status=OUT-OF-SCOPE but Reason column is empty\n", id)
      } else {
        oos_n++
      }
    } else if (status == "REQUIRED") {
      fail_n++
      printf("FAIL  %-8s status=REQUIRED — not yet migrated\n", id)
    } else {
      fail_n++
      printf("FAIL  %-8s unrecognized status \"%s\"\n", id, status)
    }
  }
  END {
    if (status_col == 0) {
      print "Could not find a Status column in the table header — check the file matches references/capability-manifest-format.md" > "/dev/stderr"
      exit 2
    }
    printf("\n%d row(s): %d DONE, %d OUT-OF-SCOPE, %d not yet terminal.\n", total, done_n, oos_n, fail_n)
    if (fail_n > 0) {
      print "Coverage check FAILED — do not report this migration finished until every row above is resolved."
      exit 1
    }
    print "Coverage check passed — every capability is DONE or explicitly OUT-OF-SCOPE."
  }
' "$MANIFEST"
