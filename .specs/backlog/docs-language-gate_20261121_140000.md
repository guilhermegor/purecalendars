# Ledger — #73 docs-language-gate

Branch: `ci/73-docs-language-gate` · Issue: #73 · Class: **ci**

## Goal

Declare the docs locale (`theme.language: en`) and adopt the BlueprintX docs-language gate.

## Work

- [x] `theme.language: en` in `mkdocs.yml`
- [x] Vendor `bin/check_docs_language.py` and its dependency `bin/check_comment_language.py`
- [x] Pre-commit hook and `tests.yaml` step, appended at the end of each list
- [x] Unit tests (`tests/unit/test_docs_language_gate.py`)
- [x] `docs/contributing.md` states the rule

## Notes

- `check_comment_language.py` is byte-identical to the copy in #65, so the merge is clean.
- The template test of `description_sources.reads_as_ptbr` was dropped; that module is #66's.
- No existing page was flagged.
