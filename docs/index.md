# **purecalendars** <img src="assets/logo_purecalendars_no_description.png" align="right" width="200" style="border-radius: 15px;" alt="purecalendars logo">

Holiday calendars and business-day arithmetic for Brazilian and US markets, computed offline.

`purecalendars` ships official holiday calendars for Brazil (ANBIMA, FEBRABAN, B3) and the United
States (Federal Holidays), then layers a rich set of working-day / date helpers on top
— `is_working_day`, `add_working_days`, `working_days_range`, `delta_working_days`,
timezone-aware conversions, and more. Every calendar is computed locally: no network, no cache.

!!! note "Renamed from `wwdates` in 3.0.0"
    Use `import purecalendars`. Since 3.0.1, `import wwdates` still works but emits a
    `DeprecationWarning`; that alias is removed in 4.0.0. The live fetchers (`*Web` classes,
    `DatesUSNasdaq`) moved to the separate `opendata-calendars` package, which returns `purecalendars` calendars.

---

## Contents

| Section | Description |
|---------|-------------|
| [Usage](usage.md) | Installation, choosing a provider, and basic examples |
| [Examples](examples.md) | Task-oriented recipes (settlement dates, expiry, cross-market) |
| [API Reference](api.md) | Public providers and every shared calendar operation |
| [FAQ](faq.md) | Common questions and troubleshooting |
| [Contributing](contributing.md) | Dev setup, testing, wheel build, PR workflow, releasing |
| [Changelog](changelog.md) | Per-version release history |

---

## Quick start

```bash
pip install purecalendars
```

```python
from datetime import date

from purecalendars.br.b3 import DatesBRB3

cls_cal = DatesBRB3()
cls_cal.is_working_day(date(2024, 12, 25))          # False — Christmas
cls_cal.add_working_days(date(2024, 12, 24), 3)     # skips holidays + weekends
cls_cal.holidays()                                  # [(name, date), ...]
```

Everything works offline after install — no network, no browser.

---

## Providers at a glance

| Country | Import | Source |
|---------|--------|--------|
| 🇧🇷 Brazil | `from purecalendars.br.anbima import DatesBRAnbima` | ANBIMA national holidays (offline, recommended) |
| 🇧🇷 Brazil | `from purecalendars.br.febraban import DatesBRFebraban` | FEBRABAN bank holidays (offline, recommended) |
| 🇧🇷 Brazil | `from purecalendars.br.b3 import DatesBRB3` | National + B3 exchange extras (offline, recommended) |
| 🇺🇸 USA | `from purecalendars.us.federal_holidays import DatesUSFederalHolidays` | US federal holidays (offline, recommended) |

---

Generated from the **lib-minimal** template via [BlueprintX](https://github.com/guilhermegor/BlueprintX).
