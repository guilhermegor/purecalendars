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
  fence without padding it, so a table right under a closer renders no table and the closer is no
  block start; a blank line after it still ends the block. The first fuzz (60000 fence-heavy
  pages) counted 91869 `_starts_table` calls, 27852 right after a fence-looking line, and no
  "table" decided through a non-closer fence line. It never looked at real closers, which is how
  it missed this.
- Line kinds Python-Markdown claims before its setext processor, and so are no setext text: a hash
  header (`^#{1,6}`, no space, no cap), a container opener, a comment, a block-level HTML tag, a
  processing instruction, `DOCTYPE` (prefix only) or `CDATA`, an indented line, and any `=` or `-`
  run (stacked underlines pair differently once a code block or list sits above). A list, quote or
  rule line is valid text, since setext is tried first. The line under a fence closer needs no
  special case: a closer starts no block.
- A `...` front-matter closer counts as a boundary only when the block is a YAML mapping, judged on
  the raw lines (MkDocs parses those; a tab is a YAML error) through one cached parse shared with
  the blanking pass.
- Setext underlines are flagged in one forward pass (`_flag_block_splits`). The recursive form
  raised `RecursionError` on about 330 stacked headers; the walk-back loop took 26 s on 5000 `===`
  lines and 251003 `_is_boundary` calls on a 1004-line page, against 1004 now.
- Fuzz, separate runs, all against Python-Markdown with the repo's extensions and 40000 pages per
  seed: an early run (alphabet of 21 line kinds) gave main 216 false passes versus 0 on the branch
  once the first review's list/quote and walk-back findings were fixed; the last three runs
  (seeds 7, 11 and 23, 38 line kinds incl. fence-then-table, `<div-x>`, `<?x?>`, DOCTYPE) gave main
  about 7450 false passes and the branch about 2500 to 2580, with 0 new-only false passes in pages
  without `<div>`. The rest are the unclosed-`<div>` family, which predates #132 and is not
  modelled.
- The closer lookup starts at line 2, as `RE_MULTILINE_BLANK` and MkDocs read it; the old
  predicate also refused a page whose line 1 was itself a closer.

Completed — kept as a record.
