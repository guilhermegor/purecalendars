# Ledger — #59 poe-task-fragments

Branch: `chore/59-poe-task-fragments` · Issue: #59 · Class: **ci**

## Goal

Replace `Makefile` and `tasks.sh` with the BlueprintX poe task fragments. Part of #56.

## Work

- [x] Confirm `origin/main` has `Makefile`/`tasks.sh` and no `poe_tasks*.toml`
- [x] Add `poethepoet>=0.35`, `poe_tasks.toml` and the test/lint/repo/docs/library fragments
- [x] Add `bin/poe_exec.sh`, `bin/test_cov.sh`, `bin/lint.sh`; refresh the vendored bin scripts and libs
- [x] Delete `Makefile`, `tasks.sh`, `bin/db.sh`, `bin/fix_playwright.sh`, `bin/ship.sh`
- [x] Take the template's `.vscode/tasks.json`
- [x] Point every `make <target>` / `tasks.sh` reference and the docs at `bash bin/poe_exec.sh <task>`
- [x] Keep `tests/conftest.py` `isolate_git_environment` and the `GIT_*` strip in `test_bin_scripts.py`

## Not done, on purpose

- Fragment tasks and `bin/lint.sh` gates whose scripts the repo does not have yet
  (`check_function_length`, `check_complexity`, `check_secrets`, `enable_*`, ...) are left out;
  they arrive with the matching template-drift sub-issues of #56.
- `bump_version` is not defined: versions are tag-driven here.
- `make ship` and `make db_*` have no poe equivalent (dropped).
