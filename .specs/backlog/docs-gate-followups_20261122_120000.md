# Ledger — #123 docs-gate follow-ups

Branch: `chore/123-docs-gate-followups` · Issue: #123 · Class: **ci**

## Goal

Close the follow-ups the #115 fallback review raised against `bin/check_docs_language.py`.

## Work

- [ ] 1. Declare `markdown` as a direct dependency
- [x] 2. `SET_PT_SHORT_WORDS`: refuted, `bin/lib/description_sources.py` reads it
- [x] 3. `_starts_table` stays linear on a run of headings
- [x] 4. A non-UTF-8 page or `mkdocs.yml` fails with the gate's own message
- [x] 5. Symlink-loop test skipped where Windows cannot create symlinks
- [x] 6. A page that opens with a thematic break is not hidden as front matter
- [ ] 7. A fence line inside an indented code block: decision recorded
- [x] 8. A line that starts with `|` outside a table is scored
- [x] 9. `docs-lang:untranslated` refused when the declared locale is `en`

## Notes

- Items 6 to 9 only make the gate stricter, so each lands as its own commit and can be reverted alone.
