# Ledger — #132 docs-gate-corners

Branch: `fix/132-docs-gate-corners` · Issue: #132 · Class: **ci**

## Goal

Close the corners of `bin/check_docs_language.py` where a real Markdown table is left unmasked
and scored as prose (a false failure, never a false pass). Follow-up to #131.

## Work

- [x] Setext underline under a block start, not only under a blank line (item 1)
- [x] Expand tabs once per page and read the expanded lines everywhere (item 2)
- [x] Front-matter opener with trailing blanks, as MkDocs' `YAML_RE` reads it (item 3)
- [x] Find the front-matter closer once per page, not once per line (item 4)
- [x] One autouse `cache_clear` fixture instead of per-test calls (item 5)
- [x] `RE_FENCE_CLOSE` as a boundary: measured, no change needed (item 6)

## Notes

- Item 6 is declined with a measurement. A fuzz of 60000 fence-heavy pages made 91869
  `_starts_table` calls, 27852 right after a fence-looking line, and none decided "table" through
  a fence line that was not a real closer. `_mask_lines` treats every fence-looking line (any
  indent) as a fence and masks what sits inside, and a closing line carries no pipe, so it
  cannot open a table.
- A header run is walked in a loop: the recursive form raised `RecursionError` on about 330
  stacked setext headers.
- The closer lookup now starts at line 2, as `RE_MULTILINE_BLANK` and MkDocs read it; the old
  predicate also refused a page whose line 1 was itself a closer.

Completed — kept as a record.
