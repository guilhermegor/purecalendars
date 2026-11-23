# Ledger — #130 docs-language gate corners

Branch: `fix/130-docs-gate-corners` · Issue: #130 · Class: **bin**

## Goal

Tighten `bin/check_docs_language.py`: table-start predecessors, a narrower boundary rule,
honest read-error wording, one front-matter parse per page. Follows #123 and PR #126.

## Work

- [x] Closing fence, one-line comment and titled link definition start a table
- [x] Thematic break needs three of one character; setext underline needs text above it;
      front matter close checked against the page's own front matter
- [x] Split "cannot be read" from "is not UTF-8 text"
- [x] Mask each page once (`lru_cache`), so the front matter is parsed once

## Not done, on purpose

- Footnote definitions and bare `<div>`: not reproducible with plain Python-Markdown (#130).

## Completed — kept as a record

All boxes ticked on PR #131; the ledger stays as the record of the work.
