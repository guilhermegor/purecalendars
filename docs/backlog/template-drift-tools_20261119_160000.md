# Ledger — #58 template-drift-tools

Branch: `chore/58-provenance-drift-tools` · Issue: #58 · Class: **ci**

## Goal

Stamp the project with its BlueprintX provenance and vendor the two template tools that compare
it with the current template (`bin/check_template_drift.py`, `bin/template_update.py`), so
alignment with the template is a report and never a hand-refined ticket again. Part of #56.

## Work

- [x] `.blueprintx-provenance.yaml`: tier `lib-minimal`, `blueprintx_commit` `12e76053` (chosen by
      measurement, see the PR body), `scaffolded_at` 2026-07-04. The current stamp format also
      carries `scaffold_commit`, so it is included.
- [x] `bin/check_template_drift.py`, `bin/template_update.py` verbatim from the template; their two
      unit-test files, tab-indented to match the project's `ruff format` setting.
- [x] `tests/conftest.py`: the template's `isolate_git_environment` autouse fixture, which the vendored
      tests need (under the commit hook `GIT_INDEX_FILE` pointed their fixture git calls at the
      real index, which they emptied; the index was restored with `git reset`).
- [x] `docs/contributing.md` and `CONTRIBUTING.md`: the stamp, how to run the tools, the four
      known limits.
- [x] The reporter runs without the content-drift `SKIPPED` notice; `template_update.py` dry run
      exits 0. `--apply` is not run in this issue.

## Not done, on purpose

- The tools run as `python bin/...` until the poe migration (#59); no task wrapper here.
- `review_bot_roster` stays `false` until the PR-gate issue (#63) lands.
- The known limits of the tools are recorded in the docs, not fixed here.
