# Guards that do not apply (#68, part of #56)

Branch: `ci/68-drop-inapplicable-guards`.

## Done

- [x] `bin/lint_deps.sh` vendored byte-identical from `blueprintx/templates/python-common`;
      `lint-deps` pre-commit hook and "Run Direct-Dependency Gate" `tests.yaml` step. deptry
      passes on `src/` with the existing `[tool.deptry.per_rule_ignores]`.
- [x] "Run Clean-Index Gate" `tests.yaml` step for `bin/check_clean_index.sh`.
- [x] Drops recorded in `docs/template-updates.md`; none of the dropped guards was vendored here.
- [x] `check_quality_rules.py` checked: it validates a BlueprintX-root file and only self-skips
      in a scaffolded project, so it is recorded as a drop.
- [x] `ca_bundle.py`, `pip_requirements.py`, `verify_venv_imports.py` kept: the bootstrap uses them.
- [x] `AGENTS.md`, `bin/CLAUDE.md`, `CONTRIBUTING.md` updated.

## Open

- [ ] Follow-up: the template's four `lint_deps.sh` integration tests need its
      `_materialise_gate_tree` helper, which this repo's `test_bin_scripts.py` lacks.
