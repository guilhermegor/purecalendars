# Ledger — #67 structure-typing-gates

Branch: `ci/67-structure-typing-gates` · Issue: #67 · Class: **ci**

## Goal

Import the scaffold's structure and typing gates, each as a pre-commit hook and a `tests.yaml` step.

## Work

- [x] `.layer-policy.yaml` adapted to `_internal`, `br`, `us`; `check_layer_imports.py` passes with no baseline
- [x] `check_dynamic_version_stub.py`, `check_typing.py`, `check_dtypes.py` (byte-identical to the template)
- [x] `[tool.commitizen]` moved to `.cz.toml`; `cz changelog --dry-run` works
- [x] `.vscode/extensions.json`
- [x] `_offline_holidays.py`: `national_holidays` gets `@type_checker`; `validate_year_range` carries a `type-checker-ok` reason (its guard raises `ValueError`)
- [x] Tests: `test_layer_imports_gate.py`, `test_dynamic_version_stub_gate.py`, `test_family_convention_example.py`
- [x] `bin/CLAUDE.md` and `CONTRIBUTING.md`: one line per gate
- [x] Dropped, with reasons in `docs/template-updates.md`: `check_provenance.py`, `check_contract_drift.py`, `pin_contract_oracle.py` (nothing to check since #97)
