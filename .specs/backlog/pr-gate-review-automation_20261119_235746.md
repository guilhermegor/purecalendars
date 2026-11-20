# Ledger — #63 pr-gate-review-automation

Branch: `chore/63-pr-gate-review-automation` · Issue: #63 · Class: **ci**

## Goal

Replace the inert `bin/pr_gate.py` port with the live BlueprintX gate and add the review
automation the scaffold ships with the review-bot roster. Part of #56.

## Work

- [x] Replace `bin/pr_gate.py` with the template's (`classify_risk` stays importable)
- [x] Add `pr-gate`, `pr-reconcile`, `review-threads`, `review-retry`, `coderabbit-trigger` workflows
- [x] Add `.coderabbit.yaml` and `.review-bots.yaml` (template roster kept)
- [x] Add `check_review_threads.py`, `retry_rate_limited_review.py`, `rerun_stale_gate_runs.sh`, `pr_reconcile.sh`
- [x] Add `required-checks.txt` and `check_required_checks_sync.py`; wire the sync gate
- [x] Add `enable_pages.sh`, `enable_repo_rules.sh`, `enable_security.sh` (shipped, not run)
- [x] Add `lint_actions.sh` and the `lint-actions` / `required-checks-sync` hooks
- [ ] Add the three template unit-test files (`test_pr_gate`, `test_review_retry`,
  `test_review_threads_gate`) — blocked on #71, see below
- [x] Install actionlint in the `tests.yaml` lint step; fix its pre-existing findings (the
  unused, invalid `ready_for_release` output; SC2046 in both release workflows)
- [x] `bin/lint_actions.sh`: replace `mapfile` with a read loop (macOS bash 3.2 safe)
- [x] Port blueprintx 976d00a (#1223, closes #1219) over the gate files: `pr_gate.py`,
  `pr-gate.yml`, `coderabbit-trigger.yml`, `check_review_threads.py`,
  `retry_rate_limited_review.py`, `pr_reconcile.sh`, `enable_repo_rules.sh`,
  `check_required_checks_sync.py`; keep only the repo-specific `required-checks.txt`
- [x] Drop `openpyxl` from the deptry DEP002 ignore list (no longer a dependency)
- [ ] Owner: run `bin/enable_repo_rules.sh` after merge (changes live rulesets)

## Not done, on purpose

- The three template test files are held back: they are space-indented, and the repo's
  `ruff.toml` still says `indent-style = "tab"`, so `ruff-format` rewrites them to tabs and
  `ruff` then raises E101 in their docstrings. They land once #71 adopts the template's
  `ruff.toml`. They pass verbatim (627 tests with the ledger tests).

- `Assertion weakening gate` is left out of `bin/required-checks.txt`: no workflow emits it yet
  (#65 ships it). A required check nothing emits blocks every merge. #65 re-adds the line.
- `review_bot_roster: true` in `.blueprintx-provenance.yaml` is owned by #58.
- `CONTRIBUTING.md` and `.github/CLAUDE.md` belong to #62; the text is in the PR body.
- `bin/lint.sh` (`poe lint`) does not call `lint_actions.sh` yet; it is outside this surface.
- Workflow files use the template names (`.yml`, kebab-case), not the `.yaml` names in the issue.
