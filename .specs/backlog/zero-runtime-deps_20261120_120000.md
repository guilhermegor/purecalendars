# Ledger — #97 zero-runtime-deps

Branch: `fix/97-zero-runtime-deps` · Issue: #97 · Class: **src**

## Goal

Owner decision (a), 2026-11-20: apply the template's zero-dependency path. Drop the placeholder
`main.py` and every vendored `_internal` module outside the public import closure, and remove
the runtime dependencies that only those modules used. Part of #56.

## Work

- [x] Compute the import closure from `__init__`, `br/`, `us/`
- [x] Delete `main.py`, `_internal/config/`, and the `_internal/utils` modules outside the closure
- [x] Replace the beartype `typing/` engine with the template's stdlib `type_checker` +
      `TypeChecker` metaclass (blueprintx#1207), keeping a stdlib `ABCTypeCheckerMeta`
- [x] Teach the stdlib checker union and generic-alias hints (keeps the public `TypeError`
      contract; `test_excel_float_to_date_none` passes unedited)
- [x] Drop `beartype`, `numpy`, `defusedxml`, `purepii-br`, `pure-schema-regimes`; regenerate
      `poetry.lock`; `deptry` clean
- [x] Record the deviations in `docs/template-updates.md`
- [x] Prove the wheel installs and imports with only its declared dependencies

## Not done, on purpose

- Upstreaming the union/generic-alias checker change to blueprintx: the coordinator files it.
- `bin/pr_gate.py` docstrings and `ruff.toml`'s `_internal/config/contracts` per-file ignore
  still name the removed directory; both are outside this branch's surface and harmless.
