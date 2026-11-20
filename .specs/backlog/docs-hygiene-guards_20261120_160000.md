# Ledger — #66 docs-hygiene-guards

Branch: `chore/66-docs-hygiene-guards` · Issue: #66 · Class: **ci**

## Goal

Import the docs and hygiene guards the BlueprintX scaffold ships, each as a pre-commit hook and a
`tests.yaml` step. Part of #56.

## Work

- [x] Vendor the seven guards and `bin/lib/description_sources.py` from the template
- [x] Wire each into `.pre-commit-config.yaml` and `tests.yaml` (clean-index is pre-push only)
- [x] Tests for four guards: identifier-masking and docs-code-refs (unit), clean-index and docs-sections (integration)
- [x] Single-source the description (`mkdocs.yml`), register `template-updates.md` in the nav
- [x] `.gitleaks.toml` allowlist for one historical false positive
- [x] `bin/CLAUDE.md` and `CONTRIBUTING.md`: one line per guard

## Not done, on purpose

- `check_readme_structure.sh` and `bin/lib/md_structure.sh` stay with #54.
- No dedicated tests for `check_docs_gap.py`, `check_secrets.sh`, `check_description_sync.sh` or `lib/description_sources.py`; CI runs them on every push.
- The GitHub About comparison skips locally (needs a token); it runs in CI.
