# Template updates

Deviations of this repository from the BlueprintX `lib-minimal` scaffold. Where the repo and
the template differ, the template wins; each exception is listed here with its reason.

## Vendored `_internal` reconciliation (#60, part of #56)

Source: BlueprintX `templates/python-common/src/utils`, `optional/typing`, `optional/ports`
and `templates/lib-minimal`, with the scaffold's import rewrite
(`utils.` -> `purecalendars._internal.utils.`).

### Adopted as the template ships them

`br_identifiers`, `dtypes`, `http_downloader`, `text`, `zip_extractor`, `tabular_reader`,
`dbapi`, `dates`, `schema_regimes`, `provenance`, `raw_workspace`, the `retry/` package
(replaces `retry.py`; `LogEmitter` and `retry_with_backoff` stay importable from
`purecalendars._internal.utils.retry`), `typing/*` (now beartype based, plus `policy.py`),
`utils/{CLAUDE,AGENTS}.md`, `config/{CLAUDE,AGENTS}.md`, `config/contracts/*`, `main.py`,
`py.typed`, `tests/unit/{test_typing,test_main,test_dates,test_schema_regimes}.py`.

**Owner decision (2026-11-19), supersedes the 2026-11-01 omission:** the example modules
`daily_cache`, `sidecar_metadata`, `xml_reader`, `schema_regimes` (the template's regime
module), `config/ports/example_port` and `main.py` are adopted. #72 closed as already shipped by #99; they are internal, so
none is exported through the public `__all__`.

### Deviations kept

| Deviation | Reason |
|---|---|
| Domain modules untouched: `calendars/*`, `parsers/*`, `logs.py`, `logs_emitter.py` | purecalendars' own code |
| Tab indentation (ruff-format, `ruff.toml`) instead of the template's spaces | repo style |
| `# ruff: noqa: E101` on the vendored files whose docstrings ruff-format tabifies | tab style turns NumPy docstring continuation lines into mixed indentation; fixing it in `ruff.toml` belongs to #61 |
| `requires-python >=3.11` (was `>=3.10`) | template floor; `purepii-br>=2` requires 3.11 |
| Added `beartype`, `numpy`, `defusedxml`, `purepii-br>=2`, `pure-schema-regimes<0.2` | needed by the adopted modules (template pins) |
| `tests/unit/test_calendar_abc.py` type-error regexes also accept `violates type hint` | the beartype engine words type errors differently. Superseded by #97: the regexes now match only `violates type hint` (the stdlib checker's wording) and, for `add_holidays`, the method's own `must be a` guard |
| `tabular_reader.int_skip_rows` not re-applied | the repo had no `tabular_reader` to carry the extension; the file is the template's |

## Zero runtime dependencies (#97, part of #56)

Owner decision (2026-11-20), supersedes the 2026-11-19 adoption above: apply the template's
`zero_dependency=y` path (blueprintx#1207). The wheel keeps only what `purecalendars`,
`purecalendars.br` and `purecalendars.us` import, directly or transitively. The `retry/`, `logs`
and `LogEmitter` notes above no longer apply.

| Deviation | Reason |
|---|---|
| `main.py` removed (with `tests/unit/test_main.py`) | placeholder `lib-minimal` stub, never used or exposed |
| `_internal/config/` absent (`contracts/`, `ports/`) | zero-dependency scaffold ships none; `contracts` pulled in `tabular_reader` and `purepii-br` |
| Removed from `_internal/utils`: `br_identifiers`, `daily_cache`, `dates`, `dbapi`, `dtypes`, `http_downloader`, `logs`, `logs_emitter`, `provenance`, `raw_workspace`, `retry/`, `schema_regimes`, `sidecar_metadata`, `tabular_reader`, `text`, `xml_reader`, `zip_extractor`, `parsers/dicts` | outside the public import closure (`tests/unit/test_dates.py` and `test_schema_regimes.py` went with them) |
| `typing/` is the template's stdlib engine (`type_checker.py`, `type_checker_meta.py`); `decorators`, `policy`, `protocol_type_checker`, `validate` removed | beartype engine replaced; `tests/unit/test_typing.py` is the template's zero-dependency test |
| `typing/abc_type_checker.py` kept, built on the stdlib `TypeChecker` | `calendars/_abc_calendar.py` uses `ABCTypeCheckerMeta`; the zero-dependency template ships no ABC variant |
| `typing/type_checker.py` also checks each member of a union (`X \| Y`, `Optional`) and the origin class of a generic alias (`list[int]` checks `list`) | the template checks plain classes only, which would drop the runtime `TypeError` on 55 of 107 annotated public parameters (every `date_: datetime \| date`); `Literal` values and container elements stay unchecked |
| `beartype`, `numpy`, `defusedxml`, `purepii-br`, `pure-schema-regimes` removed from `[tool.poetry.dependencies]` | no remaining import; `numpy` still installs transitively through `pandas` |
| The drift reporter (`bin/check_template_drift.py`) lists the removed files as missing | the stamp records no `zero_dependency` flag, so it compares against the default scaffold; it is a reporter (exit 0), the gap is intended |

## Tool configuration alignment (#61, part of #56)

Template taken verbatim: `.gitattributes`, `.gitlint`, `.hadolint.yaml`, `.pydocstyle`,
`.shellcheckrc`, `.sqlfluff`, `.sqlfluffignore`, `.yamllint`, `requirements.txt`,
`pytest.ini`, `tests/AGENTS.md`, `tests/CLAUDE.md`.

### Deviations kept

| Deviation | Reason |
|---|---|
| `.editorconfig` `[*.py]` and `.vscode/settings.json` `[python]` use tabs | `ruff.toml` formats with tabs until #71 |
| `mypy.ini` `python_version = 3.11` | pinned to the `requires-python` floor |
| `mypy.ini` drops the template's `[mypy-purecalendars.*]` ignore | first-party here; it would mask broken imports |
| `mypy.ini` adds `[mypy-businesstimedelta.*]` | the dependency ships no stubs and no `py.typed` |
| `mypy.ini` keeps `[mypy-*._internal.utils.typing.*]` `ignore_errors` | the vendored typing engine is metaprogramming |
| `mypy.ini` `[mypy-...parsers.dicts] disallow_any_explicit = False` | domain helper annotates its payload as `Any`. Removed by #97 with `parsers/dicts` |
| `tests/conftest.py` tab-indented; `isolate_git_environment` drops every `GIT_*` key | pre-commit leaks more keys than the template's seven |
| `.coveragerc` loses the `_internal/` coverage omit comment | the template has no omit; `_internal/` is now measured |
| `.gitignore` and `.codespellrc` replaced wholesale by the template | local header comments and extra ignore words dropped |
| `[tool.deptry.per_rule_ignores] DEP002` adds `tzdata` | runtime data for `zoneinfo`, never imported |

## Docs layout (#69, part of #56)

Owner decision (2026-11-01): adopt both the template's `extra.version.provider: mike` selector
(supersedes the drop in closed #14) and its logo slot (`docs/assets/logo.png` as `theme.logo` and
`theme.favicon`), filled with the real purecalendars logo rather than the placeholder.

| Deviation | Reason |
|---|---|
| `docs/stylesheets/extra.css` merged into `brand.css`, not dropped | keeps the desktop sidebar-title hiding rule |
| `docs/CLAUDE.md` holds the guidance itself instead of `@AGENTS.md` | the repo ships no `docs/AGENTS.md` |
| nav omits `Releasing 1.0.0` | the repo ships no `releasing-1-0-0.md` |
| `docs/api/reference.md` keeps the whole API reference as one page | it is the real content; the template's page is a starter |
| `docs/incidents.md` has no worked example entry | an empty record is truer than a fictional incident |
| mike selector is inert until a `mike deploy` publishes `versions.json` | `docs.yaml` deploys with Pages, not mike |

## Guards that do not apply (#68, part of #56)

Owner decision (2026-11-21): drop the guards for code this library does not have, in
purecalendars only. The BlueprintX template keeps shipping them. `bin/lint_deps.sh` (deptry) is
adopted as a pre-commit hook and a CI step. `bin/check_clean_index.sh` stays pre-push only: a
fresh CI checkout never has staged work, so a CI step could not fail.

| Not shipped | Reason |
|---|---|
| `check_sql_guards.py`, `check_orm_model_guards.py` | no SQL and no ORM models |
| `check_migration_graph.py`, `check_migration_slugs.py` | no database migrations |
| `check_rmw_race.py` | no database read-modify-write |
| `check_env_docs_sync.py` | the library ships no `.env` |
| `lint_docker.sh` | no Dockerfile |
| `export_deps.sh`, `bin/lib/wheelhouse_select.py` and its test | no wheelhouse or dependency export |
| `check_quality_rules.py` | validates `quality-rules.yaml`, which exists only at the BlueprintX root; here it could only self-skip |

`bin/lib/ca_bundle.py`, `pip_requirements.py` and `verify_venv_imports.py` stay, although the
decision listed them with the wheelhouse files: `bootstrap.sh` builds the corporate CA bundle
with the first, and `pip_fallback.sh` calls the other two when Poetry is unavailable.

## Ruff config pruning (#107)

| Deviation | Reason |
|---|---|
| `[lint.pylint] max-positional-args = 12` (template: 1); the `# noqa: PLR0917` baselines are gone | the widest public signature (`delta_working_hours`) takes 12 positionals; keyword-only would break the public API |
| `S404` no longer ignored globally; ignored under `bin/**` and `tests/**` only | no `src/` file imports `subprocess`, so the library keeps the signal |
| no-I/O banned-api block carries its explanatory comment again | AGENTS.md cites it |

Pruned because this repo has no such module:

- banned-api `utils.tabular_reader.FileContract` and `config.contracts.FileContract`
- `known-first-party`: `app`, `capabilities`, `chassis`, `config`, `controller`, `model`,
  `utils`, `view` (the whole list; ruff detects `purecalendars` from `src/`)
- per-file ignores `src/chassis/db_wschema/infrastructure/joblib_handler.py` (E101),
  `src/utils/xml_reader.py` and `src/*/_internal/utils/xml_reader.py` (N813)

Docstring parameter and return descriptions were re-indented from 8 to 4 columns under their
name line (ruff had expanded tabs to 8); code is unchanged.
