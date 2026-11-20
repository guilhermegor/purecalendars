# Ledger — #41 release-drop-group-exclusion

Branch: `chore/41-release-drop-inert-group-exclusion` · Issue: #41 · Class: **ci**

## Goal

Delete the inert `without_groups` dev/docs exclusion in the two release workflows (issue option 2).

## Work

- [x] `release-pypi.yaml`: plain `poetry install --no-interaction --no-root`, comment on why `dev` is needed
- [x] `release-test-pypi.yaml`: same

## Not done, on purpose

- The `backfill` input and jobs are untouched; #84 removes them.
- Behaviour is unchanged: the grep never matched, so the full install already ran.

## Completed — kept as a record

Option (2) chosen per the issue's stated leaning; the owner can veto at merge.
