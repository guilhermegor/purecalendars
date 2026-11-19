# Ledger — #81 release-python-minor-pin

Branch: `ci/81-release-python-minor-pin` · Issue: #81 · Class: **ci**

## Goal

Unblock the purecalendars 3.0.0 release. The Test PyPI run (44515729261) passed every test,
then failed in `setup_and_build`: setup-python has no 3.12.8 build for Ubuntu 26.04, which
`ubuntu-latest` now resolves to. No tag was created.

## Work

- [x] `release-pypi.yaml` and `release-test-pypi.yaml` pin `["3.12"]`, as the BlueprintX
      lib-minimal template already does. setup-python then resolves the newest 3.12 patch
      available for the runner image.
- [x] `tests/integration/test_ledger_gate_cli.py` drops inherited `GIT_*` variables before its
      nested git calls. From inside the pre-commit hook, `GIT_INDEX_FILE` pointed the throwaway
      repo's `git commit` at the outer index, so the suite failed only when run from the hook.
      It reproduces standalone with `GIT_INDEX_FILE=$PWD/.git/index`.

## Verification

- [x] `tests/integration/test_ledger_gate_cli.py` passes with `GIT_INDEX_FILE` set.
- [ ] Test PyPI 3.0.0 rerun green.
