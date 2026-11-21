# Ledger — #107 prune-ruff-config

Branch: `chore/107-prune-ruff-config-docstring-indent` · Issue: #107 · Class: **src**

## Goal

Follow-ups deferred from the #104 review: prune template-only `ruff.toml` entries, restore the
no-I/O banned-api comment, relax PLR0917 instead of breaking the public API, re-indent
docstring descriptions from 8 to 4 columns, and point `docs/contributing.md` at `ruff.toml`.

## Work

- [x] Prune dead banned-api, `known-first-party` and per-file entries; record them
- [x] Raise `max-positional-args` to 12 and drop the `# noqa: PLR0917` baselines
- [x] Scope the S404 ignore to `bin/**` and `tests/**`
- [x] Restore the no-I/O comment above the banned-api block
- [x] Re-indent docstrings to 4 columns (AST compare: only docstrings changed)
- [x] Replace the rule-family list in `docs/contributing.md` with a pointer

## Not done, on purpose

- Keyword-only arguments: a public API break, rejected by the owner.
