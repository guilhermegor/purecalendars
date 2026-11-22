# AGENTS.md

Guidance for agents working in this repository.

## Engineering principles

Read `PRINCIPLES.md` for the single-responsibility and function-design rules this project follows.

## Shared conventions

The boundary rules, data-handling guardrails, runtime type-checking notes, naming and
file-naming conventions, tooling summary and the project-memory rule are shared by every
BlueprintX skeleton and live in `.claude/CLAUDE.md` (single source:
`templates/common/CLAUDE.md`). Read that file before editing code: only Claude Code
loads it on its own, other agents must be told to. This file keeps only what is
specific to this skeleton.

⚠️ The shared boundary rule 1 (the seam knows the vendor) has one tier-specific twist here:
a caller imports the seam **package-qualified** —
`from purecalendars._internal.utils.calendars import DateFormatter` — never a bare
`from utils…`, which resolves only by accident of `sys.path` and breaks once the wheel is
installed.

## What this template is

A **PyPI-ready Python library starter**. A clean, importable package with CI, pre-commit,
tests, docs, and PyPI + Test-PyPI release workflows ready to go. It is scaffolded by
BlueprintX into a new project directory; the scaffold replaces the `<project_name>` package
directory and the `pyproject.toml` placeholders via `envsubst`.

## Layout

```
src/<project_name>/
    __init__.py            # the public API surface (control it with __all__)
    abc_calendar_operations.py  # ABCCalendarOperations, the public base class to subclass
    br/  us/               # public calendar providers, one subpackage per country
    _internal/             # PRIVATE — ships in the wheel, but not a public API
        utils/             # calendars/ (the mixin chain), parsers/str.py, and typing/
                           #   (stdlib runtime type checker — no third-party dependency)
                           # no config/: zero-dependency path (#97, docs/template-updates.md)
tests/
    unit/  integration/  performance/
```

**Public vs private.** Consumers import `<project_name>` (your core). Everything under
`<project_name>._internal` is vendored support code: it ships inside the wheel (so imports
resolve after `pip install`), but the leading underscore marks it off-limits — keep it out
of your public `__all__`. The internal imports are package-qualified
(`from purecalendars._internal.utils.calendars import …`).

**Consumer-built schema models stay in `_internal/config/schemas/`.** When the models are the
library's product (consumers construct them), the file location is still an implementation
detail: re-export each class from the package `__all__` and let consumers write
`from <project_name> import X`, never the `_internal` path. Do not move them to a public
`schemas/` package. Accepted cost: the class's `__module__` (tracebacks, mkdocstrings paths,
pickles) shows the `_internal` path, so moving the file later is a pickle-compatibility change.

## Architecture

- **One public class per module/file.** The public class is named after the file
  (`user_service.py` → `UserService`). When helpers share no state and need no lifecycle,
  prefer **module-level functions** over a utility class. A private/shared base class gets
  its **own** `_`-prefixed file (`_base_reader.py`) — never share a module with a public
  class.
- **Separate I/O from logic**: pure functions in the core, side effects at the edges.
- Reach for a class only when there is **state + lifecycle**, **interface conformance**, or
  **dependency injection** — otherwise a module of functions is the right shape.
- **No redundant package-name subfolder.** When the package's whole purpose is one domain
  (e.g. `calendars`), do **not** nest a subfolder that repeats the package name
  (`src/<project_name>/<project_name>-ish/`) — the package name already conveys the scope. Public
  providers live in the country subpackages (`src/purecalendars/br/`, `src/purecalendars/us/`,
  imported as `purecalendars.br` / `purecalendars.us`), and the public base class every provider
  extends is `src/purecalendars/abc_calendar_operations.py`; put non-exported abstract bases /
  internals under `_internal/`.
- **On migration, reuse the target's own implementation.** When lifting code in from another
  repo, if this project already has an equivalent module (its own `_internal` typing engine, a
  helper), rewrite the imports to **this** project's version and discard the source's duplicate —
  never vendor a second copy (DRY). The scaffold's own `rewrite_internal_imports` embodies this.

## Conventions (inherited from `templates/python-common/`)

- **Ruff**: linter + formatter. Line-length 99, double quotes, NumPy docstrings, 4-space
  indent (`ruff.toml` is the template's).
- **Pre-commit**: ruff, pydocstyle, codespell, commitizen, gitlint, unit + integration
  tests, coverage badge.
- **Tests**: `pytest` — `bash bin/poe_exec.sh unit_tests` (`pytest tests/unit/`). Write
  pytest-style functions with fixtures, not `unittest.TestCase`.
- **purecalendars does no file or database I/O** (`ruff.toml` bans the bare pandas readers).
  Live and tabular sources are read in `opendata-calendars`, which depends on this package,
  never the reverse. Do not add reads here, and do not re-vendor the template's I/O toolkit
  (`tabular_reader`, `dtypes`, `br_identifiers`, ...): #97 removed it with its dependencies.
- **No `.env`** — a distributable library has no runtime env to seed (unlike the service
  tiers), so none is shipped. This does not block the opt-in OTLP log exporter
  (`_internal/utils/otel_logging.py`, blueprintx#438): it reads
  `OTEL_EXPORTER_OTLP_ENDPOINT` etc. from the **consumer's own process environment** at call
  time — the same "the host configures the env, the library ships no file" pattern
  `ts_lib.sh` already uses. `configure_otel_logging(logger)` is injected, never auto-run on
  import, matching the dependency-injection rule below.
- **Logging via dependency injection** — never hard-import a logging backend in a helper;
  inject a logger (stdlib default), as the calendar providers' `logger: Logger | None`
  constructor argument does.
- **Every imported package is a direct dependency.** If a module `import`s a package, declare
  it in `pyproject.toml` — even when it is already installed transitively via another dep. A
  transitive presence is an accident of another package's tree and breaks silently the day that
  package drops or version-caps it. Run `poetry add <pkg>` for anything you import.

  **Enforced**: `bin/lint_deps.sh` runs `deptry` over `src/` as the `lint-deps` pre-commit
  hook and a `tests.yaml` step, configured under `[tool.deptry.per_rule_ignores]`. Two things
  worth knowing:

  - **A guarded import is still an import.** `try: import numpy / except ModuleNotFoundError:`
    degrades gracefully at runtime and changes nothing about the declaration — that pattern is
    why `numpy` went undeclared for as long as it did.
  - **Configuration lives in `pyproject.toml`'s `[tool.deptry]` block, never in a shared
    `deptry.toml`.** deptry takes its dependency list from the same file it takes its settings
    from, so `--config <other>` silently re-points it at a manifest that declares nothing.

## Work trackers (`.specs/`)

`docs/` is published documentation only. Working material lives in `.specs/` (see
`.specs/CLAUDE.md`): `features/<name>/{design,plan,tasks}.md` per feature, and a flat
`backlog/<kebab-topic>_YYYYMMDD_HHMMSS.md` for work spanning no single feature. A branch touching
`src/` or CI paths must add a flat `.specs/backlog/` ledger with a checkbox
(`bin/check_backlog_ledger.py`); `bin/check_specs_structure.sh` and `bin/check_docs_boundary.sh`
enforce the layout. Trackers are never deleted — tick the last box and add a
"Completed — kept as a record" note.

## Releasing to PyPI

Two workflows ship under `.github/workflows/`:

- `release-test-pypi.yaml` — publish to **Test PyPI** first (`workflow_dispatch`).
- `release-pypi.yaml` — publish to **PyPI** and cut a GitHub release.

**Versioning is tag-driven.** `[tool.poetry] version` is a `0.0.0` placeholder;
**poetry-dynamic-versioning** stamps the real version from the git tag at build time (`python -m
build`, not `poetry build`). There is **no `bump_version` task**. To release, dispatch the
workflow with the version: it runs the full test suite as a hard gate, gates on the version
being greater than what is already published, builds with the requested version stamped through
`POETRY_DYNAMIC_VERSIONING_BYPASS` (so a re-run never collides with an existing tag), uploads
through **OIDC trusted publishing** (`pypa/gh-action-pypi-publish`, `id-token: write`) — no API
token stored. A separate `github_release` job tags the commit `vX.Y.Z` and cuts the GitHub
release. The `pypi` and `github_release` jobs both depend on `setup_and_build`, not on each
other, so a failed PyPI publication does not stop the GitHub release: check both job results.

Configure a GitHub Environment per index (**`release-pypi`** for PyPI, **`release-test-pypi`**
for Test PyPI) and a **trusted publisher** on each index matching owner `guilhermegor`, repo
`purecalendars`, the respective workflow filename, and its matching environment; for a
first-ever release register a **pending publisher**. The changelog is generated from tags by
`cz changelog` at docs-build time, never committed to `main` by CI. See `docs/contributing.md`.

The docs are **not** versioned with `mike` here: `docs.yaml` builds the site and deploys it with
GitHub Pages on every push to `main` (no `gh-pages` branch, no `poe enable_pages`). The
template's mike selector is adopted but inert until a `mike deploy` publishes `versions.json`
(`docs/template-updates.md`, "Docs layout").

## Extending this template

- Keep `src/<project_name>/` as the importable package root; grow the public API there.
- Add sub-packages as the project grows — do not dump everything into one module.
- Mirror the test folder hierarchy to match the package structure.
