# Ledger — #76 rename-to-purecalendars

Branch: `chore/76-rename-to-purecalendars` · Issue: #76 · Class: **src**

Code half of #75; it also touches the release workflows (ci).

## Goal

Ship `purecalendars` 3.0.0: the distribution and the import package renamed together from
`wwdates`, with every I/O module removed so the package fits the `pure*` family rule
(computation only, no I/O). The I/O half becomes `opendata-calendars` (guilhermegor/greenfield#103).

## Work

- [x] `src/wwdates` → `src/purecalendars`; `version("purecalendars")` in `__init__.py`, changed in
      the same commit as the dist name so `__version__` cannot fall back to `0.0.0`.
- [x] Removed the I/O side, measured by the import closure of the offline modules: `*_web.py`,
      `us/nasdaq.py`, `cache/`, `http_downloader.py`, `webdriver_tools/`, `parsers/html.py`,
      `tabular_reader.py`, `zip_extractor.py`, `_internal/config/`, `bin/check_calendar_drift.py`
      and the `calendar-drift` workflow, with their tests.
- [x] Dropped `requests`, `lxml`, `openpyxl`, `xlrd`, `playwright` and the `web` extra.
- [x] `ruff.toml`: the pandas-reader ban now states the no-I/O rule.
- [ ] Release workflows renamed to the hyphenated names the OIDC publishers were registered with
      (`release-pypi.yaml` / `release-test-pypi.yaml`, environments `release-pypi` /
      `release-test-pypi`), `PACKAGE_NAME` updated.
- [ ] `backfill` input on both release workflows (opendata-cvm#419 mechanism) so v0.1.0–v2.0.0
      are rebuilt under the new name, keeping the old name literal for historical tags.
- [ ] README, `docs/`, `CLAUDE.md`, `CONTRIBUTING.md` describe the offline-only package.

## Why the I/O leaves instead of staying behind an extra

`pip install purecalendars` must not pull `requests`, Playwright or a disk cache. An extra would
keep the code in the `pure*` package and need an exception to the family rule; the owner chose
the split (2026-11-18, #75). `opendata-calendars` depends on `purecalendars`, never the reverse.

## What is not lost

The removed modules and their tests stay at tag `v2.0.0`, and the backfilled `purecalendars`
2.0.0 on PyPI still ships them. greenfield#103 recovers them with `git show v2.0.0:<path>`.
The weekly drift job is paused until then.

## Historical record left untouched

`docs/backlog/*`, `docs/checkpoints.md` and the changelog history keep the name `wwdates`: they
record what happened under that name, and GitHub redirects the old links.

## Verification

- [x] `poetry run pytest tests` — 227 passed.
- [x] `ruff check`, `ruff format --check`, `mypy src` — clean.
- [x] No `requests`/`urllib`/`http`/`socket`/`playwright`/`lxml`/`pickle`/`zipfile`/`csv` import
      left under `src/`.
- [ ] Test PyPI rehearsal, then PyPI, install-verified (`pip install purecalendars`,
      `import purecalendars`).

## Deferred (tracked here, not in this PR)

- Downstream moves (blueprintx#1212, `~/dev` consumers, board, `roadmap_unblock.sh`) — #75.
- Deleting the old `wwdates` projects on Test PyPI and PyPI — owner, after consumers move (#75).
