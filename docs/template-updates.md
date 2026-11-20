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
module), `config/ports/example_port` and `main.py` are adopted. #72 deletes them at 4.0.0, so
none is exported through the public `__all__`.

### Deviations kept

| Deviation | Reason |
|---|---|
| Domain modules untouched: `calendars/*`, `parsers/*`, `logs.py`, `logs_emitter.py` | purecalendars' own code |
| Tab indentation (ruff-format, `ruff.toml`) instead of the template's spaces | repo style |
| `# ruff: noqa: E101` on the vendored files whose docstrings ruff-format tabifies | tab style turns NumPy docstring continuation lines into mixed indentation; fixing it in `ruff.toml` belongs to #61 |
| `requires-python >=3.11` (was `>=3.10`) | template floor; `purepii-br>=2` requires 3.11 |
| Added `beartype`, `numpy`, `defusedxml`, `purepii-br>=2`, `pure-schema-regimes<0.2` | needed by the adopted modules (template pins) |
| `tests/unit/test_calendar_abc.py` type-error regexes also accept `violates type hint` | the beartype engine words type errors differently |
| `tabular_reader.int_skip_rows` not re-applied | the repo had no `tabular_reader` to carry the extension; the file is the template's |

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
| `mypy.ini` `[mypy-...parsers.dicts] disallow_any_explicit = False` | domain helper annotates its payload as `Any` |
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
