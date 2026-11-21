# Ledger — #71 adopt-template-ruff

Branch: `style/71-adopt-template-ruff` · Issue: #71 · Class: **src**

## Goal

Adopt the BlueprintX `ruff.toml` and reformat the tree. Part of #56.

## Work

- [x] Replace `ruff.toml` with the template's (python-common at blueprintx main)
- [x] `ruff format` src, tests and bin (tab to space)
- [x] Baseline the new-rule findings with `ruff --add-noqa` (no logic edits)
- [x] Update `.editorconfig`, `CONTRIBUTING.md` and `docs/contributing.md`
- [ ] Re-format `bin/*.py` added by #102 once it merges

## Not done, on purpose

- No comment-budget gate or baseline file exists in this repo yet, so there is
  nothing to re-baseline.
- The baselined `PLR6301` / `PLR0917` findings need signature changes
  (`@staticmethod`, keyword-only arguments); that is a behaviour change.
- `.vscode/settings.json` still sets tab indentation for Python (outside the
  #71 surface).
