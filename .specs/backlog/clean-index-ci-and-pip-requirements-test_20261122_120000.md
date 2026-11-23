# Ledger — #68 clean-index CI step and pip_requirements tests

Branch: `chore/clean-index-ci-and-pip-requirements-test` · Issue: #68 (Refs, not closed) · Class: **ci**

## Goal

Land the two items the owner ruled on in #68 (comment 7088414522): run the clean-index check in CI,
and give `bin/lib/pip_requirements.py` a unit test.

## Work

- [x] Add a clean-index step to `tests.yaml` on one cell (ubuntu, Python 3.11), with a negative control
- [x] Update `docs/template-updates.md` and `bin/CLAUDE.md`, which said "pre-push only"
- [ ] Add `tests/unit/test_pip_requirements.py`, one assert per test

## Completed — kept as a record

Pending.
