<!-- readme-archetype: library -->
# purecalendars

<p align="center"><img src="https://raw.githubusercontent.com/guilhermegor/purecalendars/main/assets/logo_purecalendars_no_description.png" width="200" alt="purecalendars"></p>

[![Project Status: Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)
[![PyPI Version](https://img.shields.io/pypi/v/purecalendars)](https://pypi.org/project/purecalendars/)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue)](https://guilhermegor.github.io/purecalendars/)
[![Linting](https://img.shields.io/badge/linting-ruff_%7C_codespell-blue)](https://github.com/astral-sh/ruff)
[![Type-checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy-lang.org/)
![Test Coverage](https://raw.githubusercontent.com/guilhermegor/purecalendars/main/coverage.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Open Issues](https://img.shields.io/github/issues/guilhermegor/purecalendars)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-darkgreen.svg)

<!-- slug: overview -->
## Overview

Holiday calendars and business-day arithmetic for Brazilian and US markets, computed offline.

`purecalendars` ships official holiday calendars for Brazil (ANBIMA, FEBRABAN, B3) and the United
States (Federal Holidays), then layers a rich set of working-day / date helpers on top —
`is_working_day`, `add_working_days`, `working_days_range`, `delta_working_days`, timezone-aware
conversions, and more. Every calendar is computed locally: no network, no cache, no browser.

> The live fetchers (`*Web` classes, `DatesUSNasdaq`) moved to the separate
> [`opendata-calendars`](https://github.com/guilhermegor/greenfield/issues/103) package, which
> returns `purecalendars` calendars.

<!-- slug: features -->
## Key Features

### Holiday providers

One class per calendar source; all share the same date-operations surface — they differ only in
**which** holidays they load.

| Provider                 | Import                              | Holidays                                |
| ------------------------ | ----------------------------------- | --------------------------------------- |
| `DatesBRAnbima`          | `purecalendars.br.anbima`           | ANBIMA national holidays                |
| `DatesBRFebraban`        | `purecalendars.br.febraban`         | FEBRABAN bank holidays                  |
| `DatesBRB3`              | `purecalendars.br.b3`               | National + B3 exchange non-trading days |
| `DatesUSFederalHolidays` | `purecalendars.us.federal_holidays` | US federal holidays (statutory + observed) |

### Shared calendar operations

Every provider inherits the full surface: working-day predicates (`is_working_day`, `is_holiday`,
`is_weekend`), business-day arithmetic (`add_working_days`, `nearest_working_day`,
`get_nth_weekday_month`), ranges & deltas (`working_days_range`, `delta_working_days`,
`delta_working_hours`), timezone/timestamp conversions, and locale-aware formatting. See the
[API Reference](https://guilhermegor.github.io/purecalendars/api/) for the complete list.

<!-- slug: documentation -->
## Documentation

The full documentation is published at <https://guilhermegor.github.io/purecalendars/>:

- [Usage](https://guilhermegor.github.io/purecalendars/usage/) — install, providers, basics
- [Examples](https://guilhermegor.github.io/purecalendars/examples/) — task-oriented recipes
- [API Reference](https://guilhermegor.github.io/purecalendars/api/) — every class and method
- [FAQ](https://guilhermegor.github.io/purecalendars/faq/) — common questions & troubleshooting
- [Contributing](https://guilhermegor.github.io/purecalendars/contributing/) — dev setup, tests, releasing
- [Changelog](https://guilhermegor.github.io/purecalendars/changelog/) — release history

<!-- slug: getting-started -->
## Getting Started

Python 3.11+ is the only prerequisite; Poetry is recommended.

<!-- slug: install -->
### Install

```bash
pip install purecalendars
```

Or with Poetry:

```bash
poetry add purecalendars
```

Everything works offline after install — no network, no browser.

<!-- slug: usage -->
### Usage

```python
from datetime import date

from purecalendars.br.b3 import DatesBRB3

cls_cal = DatesBRB3()
cls_cal.is_working_day(date(2024, 12, 25))       # False — Christmas
cls_cal.add_working_days(date(2024, 12, 24), 3)  # skips holidays + weekends
cls_cal.holidays()                               # [(name, date), ...]
```

`DatesBRB3` here is just an example — the same methods work on every provider; only the loaded
holiday set differs. More recipes in the
[Examples](https://guilhermegor.github.io/purecalendars/examples/) guide.

<!-- slug: project-structure -->
## Project Structure

```text
purecalendars/
├── .github/              workflows, CODEOWNERS, PR template
├── .specs/               work ledgers and specs
├── assets/               logo
├── bin/                  gate scripts and helpers
├── docs/                 published documentation (mkdocs)
├── src/purecalendars/
│   ├── br/               ANBIMA, FEBRABAN and B3 calendars
│   ├── us/               US federal holidays
│   └── _internal/        private: vendored helpers
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── poe_tasks.toml        task runner entry points
```

<!-- slug: development -->
## Development

```bash
git clone https://github.com/guilhermegor/purecalendars.git
cd purecalendars
bash bin/venv.sh                            # create the venv and install dependencies
bash bin/poe_exec.sh init                   # seed .env, install pre-commit hooks
bash bin/poe_exec.sh unit_tests             # run the test suite
bash bin/poe_exec.sh install_dist_locally   # build the wheel and smoke-import it
```

See [Contributing](https://guilhermegor.github.io/purecalendars/contributing/) for the full branch/PR
workflow and CI gate.

<!-- slug: public-api -->
## Public API

The package root exports `__version__` and `ABCCalendarOperations`, the base class to subclass for
your own calendar; each provider is imported from its own module. Nothing under `_internal/` is
public; `ABCCalendarOperations` lives in the public `purecalendars.calendar_operations` module and
is re-exported from the root:

- `purecalendars.ABCCalendarOperations`
- `purecalendars.br.anbima.DatesBRAnbima`
- `purecalendars.br.febraban.DatesBRFebraban`
- `purecalendars.br.b3.DatesBRB3`
- `purecalendars.us.federal_holidays.DatesUSFederalHolidays`

<!-- slug: publishing -->
## Publishing

Releases are cut by dispatching the release workflows under `.github/workflows/` with a version
input, and go out through PyPI trusted publishing (OIDC); the `vX.Y.Z` tag records the release.

<!-- slug: contributing -->
## Contributing

Issues and PRs are welcome. Please read [`CONTRIBUTING.md`](https://github.com/guilhermegor/purecalendars/blob/main/CONTRIBUTING.md) first for dev setup,
tests, the branch/PR workflow, and the CI gate.

<!-- slug: license -->
## License

This project is licensed under the **MIT** License — see [`LICENSE`](https://github.com/guilhermegor/purecalendars/blob/main/LICENSE) for details.

<!-- slug: authors -->
## Authors

- Guilherme Rodrigues — [GitHub](https://github.com/guilhermegor) | [LinkedIn](https://www.linkedin.com/in/guilhermegor/)

<!-- slug: useful-links -->
## Useful Links

- [Documentation](https://guilhermegor.github.io/purecalendars/)
- [PyPI](https://pypi.org/project/purecalendars/)
- [GitHub Repository](https://github.com/guilhermegor/purecalendars)
- [Issue Tracker](https://github.com/guilhermegor/purecalendars/issues)

---

<sub>Generated from the lib-minimal template via [BlueprintX](https://github.com/guilhermegor/blueprintx).</sub>
