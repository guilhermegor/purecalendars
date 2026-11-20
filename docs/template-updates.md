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
