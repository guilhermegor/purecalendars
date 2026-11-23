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
- [x] `RE_FENCE_CLOSE` as a boundary: measured; under superfences a fence closer starts no block, so
  it is no longer a boundary for tables (item 6)

## Notes

- Item 6 first read as no change needed; the fifth review showed otherwise. Superfences stashes a
  fence without padding it, so a table right under a closer renders no table, and the closer is
  no block start. The first fuzz (60000 pages) only looked at non-closer fence lines and so missed
  it. It made 91869
  `_starts_table` calls, 27852 right after a fence-looking line, and none decided "table" through
  a fence line that was not a real closer. `_mask_lines` treats every fence-looking line (any
  indent) as a fence and masks what sits inside, and a closing line carries no pipe, so it
  cannot open a table.
- A hash header is `^#{1,6}` as Python-Markdown reads it (column 0, no space, no cap), not the
  CommonMark shape; a `...` closer counts as a boundary only when the block is a YAML mapping.
- The front-matter mapping verdict reads the raw lines (MkDocs parses those; a tab is a YAML error), and
  a processing instruction, `DOCTYPE` or `CDATA` line is no setext text.
- Setext underlines are flagged in one forward pass (`_flag_block_splits`): the recursive form raised
  `RecursionError` on about 330 stacked headers, and the walk-back loop took 26 s on 5000 `===`
  lines. An ATX heading, comment, container opener, indented line or short `=`/`-` run is no
  setext text line, nor is any line starting with `#` (no space needed, any count), a block-level
  HTML tag, or the line under a fence delimiter; a list, quote or rule line is (Python-Markdown
  tries setext first). An unclosed `<div>` still swallows a later table on main and here: that
  family predates #132 and is not handled.
- The closer lookup now starts at line 2, as `RE_MULTILINE_BLANK` and MkDocs read it; the old
  predicate also refused a page whose line 1 was itself a closer.

Completed — kept as a record.
