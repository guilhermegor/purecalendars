# Ledger — #62 repo-policy-workflows

Branch: `chore/62-repo-policy-workflows` · Issue: #62 · Class: **ci**

## Goal

Import the BlueprintX repo-policy workflows, scripts and forms. Part of #56.

## Work

- [x] Compare every surface file with `templates/common` at BlueprintX `origin/main` and record the differences in the PR body
- [x] Add `branch-has-issue`, `close-linked-issues`, `dependabot-auto-merge`, `pr-body-template`, `pr-title-conventional` workflows, verbatim
- [x] Add `bin/check_pr_policy.sh`, `bin/close_linked_issues.sh`, `bin/dependabot_auto_merge.sh`, verbatim
- [x] Add integration tests for the three scripts to `tests/integration/test_bin_scripts.py`
- [x] Add `.github/ISSUE_TEMPLATE/feature_or_fix.md`; take the template's `PULL_REQUEST_TEMPLATE.md` (`tests.yml` -> `tests.yaml`)
- [x] Merge `.github/dependabot.yml` (keep the Poetry block; take assignees, cooldown and the `actions` group name)
- [x] Render `SECURITY.md`
- [x] Rewrite `.github/CLAUDE.md` and `CONTRIBUTING.md`: what happens to a PR after it opens
- [ ] Owner: enable *Allow auto-merge* and required checks (see below)

## Not done, on purpose

- `pr-self-assign.yml`: the template folded self-assignment into `branch-has-issue.yml` (a separate workflow raced the check on `opened`), so the issue's sixth workflow does not exist upstream.
- `delete-closed-pr-branch.yml` and `bin/delete_closed_pr_branch.sh`: the scaffold ships them but they are outside this issue's surface; a follow-up should decide whether to add them.
- `.github/AGENTS.md`: the repo has no `AGENTS.md`/`CLAUDE.md` pair anywhere, so `.github/CLAUDE.md` stays a standalone file instead of the template's `@AGENTS.md` pointer.
- `bin/pr_gate.py` still says "there is no auto-merge in purecalendars"; it belongs to #63 and is now stale for Dependabot PRs.
- Workflow `name:`/job `name:` values were not changed, so any required-check names registered later must use the template's names.
