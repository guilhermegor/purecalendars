# purecalendars <img src="assets/logo_purecalendars_no_description.png" align="right" width="200" style="border-radius: 15px;" alt="purecalendars">

[![Project Status: Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
[![Linting](https://img.shields.io/badge/linting-ruff_|_codespell-blue)](https://github.com/astral-sh/ruff)
[![Type-checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy-lang.org/)
![Test Coverage](./coverage.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Open Issues](https://img.shields.io/github/issues/guilhermegor/purecalendars)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-darkgreen.svg)

Holiday calendars and business-day arithmetic for Brazilian and US markets, computed offline.

`purecalendars` ships official holiday calendars for Brazil (ANBIMA, FEBRABAN, B3) and the United
States (Federal Holidays), then layers a rich set of working-day / date helpers on top —
`is_working_day`, `add_working_days`, `working_days_range`, `delta_working_days`, timezone-aware
conversions, and more. Every calendar is computed locally: no network, no cache, no browser.

> **Renamed from `wwdates` in 3.0.0.** `import wwdates` becomes `import purecalendars`. The live
> fetchers (`*Web` classes, `DatesUSNasdaq`) moved to the separate
> [`opendata-calendars`](https://github.com/guilhermegor/greenfield/issues/103) package, which
> returns `purecalendars` calendars.

📖 **Full documentation:** <https://guilhermegor.github.io/purecalendars/>

## ✨ Key Features

### 🗓️ Holiday providers

One class per calendar source; all share the same date-operations surface — they differ only in
**which** holidays they load.

| Provider                 | Import                              | Holidays                                     |
| ------------------------ | ----------------------------------- | -------------------------------------------- |
| `DatesBRAnbima`          | `purecalendars.br.anbima`           | 🇧🇷 ANBIMA national holidays                  |
| `DatesBRFebraban`        | `purecalendars.br.febraban`         | 🇧🇷 FEBRABAN bank holidays                    |
| `DatesBRB3`              | `purecalendars.br.b3`               | 🇧🇷 National + B3 exchange non-trading days   |
| `DatesUSFederalHolidays` | `purecalendars.us.federal_holidays` | 🇺🇸 US federal holidays (statutory + observed) |

### ⚙️ Shared calendar operations

Every provider inherits the full surface: working-day predicates (`is_working_day`, `is_holiday`,
`is_weekend`), business-day arithmetic (`add_working_days`, `nearest_working_day`,
`get_nth_weekday_month`), ranges & deltas (`working_days_range`, `delta_working_days`,
`delta_working_hours`), timezone/timestamp conversions, and locale-aware formatting. See the
[API Reference](https://guilhermegor.github.io/purecalendars/api/) for the complete list.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Poetry (recommended)

### Installation

```bash
pip install purecalendars
```

Or with Poetry:

```bash
poetry add purecalendars
```

Everything works offline after install — no network, no browser.

### Quick start

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

## 📚 Documentation

- [Usage](https://guilhermegor.github.io/purecalendars/usage/) — install, providers, basics
- [Examples](https://guilhermegor.github.io/purecalendars/examples/) — task-oriented recipes
- [API Reference](https://guilhermegor.github.io/purecalendars/api/) — every class and method
- [FAQ](https://guilhermegor.github.io/purecalendars/faq/) — common questions & troubleshooting
- [Contributing](https://guilhermegor.github.io/purecalendars/contributing/) — dev setup, tests, releasing
- [Changelog](https://guilhermegor.github.io/purecalendars/changelog/) — release history

## 🛠️ Development

```bash
git clone https://github.com/guilhermegor/purecalendars.git
cd purecalendars
make init                  # or: bash tasks.sh init  (venv + deps + pre-commit hooks)
make unit_tests            # run the test suite
make install_dist_locally  # build the wheel and smoke-import it
```

See [Contributing](https://guilhermegor.github.io/purecalendars/contributing/) for the full branch/PR
workflow and CI gate.

## 👨‍💻 Authors

**Guilherme Rodrigues**  
[![GitHub](https://img.shields.io/badge/GitHub-guilhermegor-181717?style=flat&logo=github)](https://github.com/guilhermegor)  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Guilherme_Rodrigues-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/guilhermegor/)

## 🔗 Useful Links

- [Documentation](https://guilhermegor.github.io/purecalendars/)
- [GitHub Repository](https://github.com/guilhermegor/purecalendars)
- [Issue Tracker](https://github.com/guilhermegor/purecalendars/issues)

## 🤝 Contributing

Issues and PRs are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) first for dev setup,
tests, the branch/PR workflow, and the CI gate.

## 📜 License

This project is licensed under the **MIT** License — see [`LICENSE`](LICENSE) for details.
