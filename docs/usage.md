# **Usage**

Installing and using `purecalendars`.

> **See also:** [API Reference](api/index.md) for the full method list · [Contributing](contributing.md)
> to develop or release the library.

---

## Installation

```bash
pip install purecalendars
```

Or with Poetry:

```bash
poetry add purecalendars
```

Everything works offline after install — no network, no browser.

---

## Choosing a provider

Every provider exposes the same calendar-operations surface (see [API Reference](api/index.md)); they
differ only in **which** holidays they load.

Every provider is computed offline. For the publishers' own live tables, use the separate `opendata-calendars` package.

```python
from purecalendars.br.anbima import DatesBRAnbima      # ANBIMA national holidays
from purecalendars.br.febraban import DatesBRFebraban  # FEBRABAN bank holidays
from purecalendars.br.b3 import DatesBRB3              # national + B3 exchange extras
from purecalendars.us.federal_holidays import DatesUSFederalHolidays  # US federal holidays
```

You can also import from the country package:

```python
from purecalendars.br import DatesBRAnbima, DatesBRB3, DatesBRFebraban
from purecalendars.us import DatesUSFederalHolidays
```

---

## Working with business days

```python
from datetime import date

from purecalendars.br.b3 import DatesBRB3

cls_cal = DatesBRB3()

cls_cal.is_working_day(date(2024, 12, 25))   # False — Christmas
cls_cal.is_holiday(date(2024, 12, 25))       # True
cls_cal.is_weekend(date(2024, 12, 28))       # True — Saturday

# Add three business days, skipping weekends and holidays.
cls_cal.add_working_days(date(2024, 12, 24), 3)     # -> date(2024, 12, 30)

# Nearest business day on or after (or before) a given date.
cls_cal.nearest_working_day(date(2024, 12, 25), bool_next=True)

# Count / list business days in a range.
cls_cal.delta_working_days(date(2024, 12, 1), date(2024, 12, 31))
cls_cal.working_days_range(date(2024, 12, 1), date(2024, 12, 31))
```

`DatesBRB3` here is just an example — the same methods work on every provider
(`DatesBRAnbima`, `DatesBRFebraban`, `DatesUSFederalHolidays`); only the loaded holiday set differs. See the [API Reference](api/index.md) for the full list of classes and
their shared methods.

---

## Listing holidays

Every provider returns `(name, date)` tuples:

```python
from purecalendars.us.federal_holidays import DatesUSFederalHolidays

for name, day in DatesUSFederalHolidays().holidays():
    print(day, name)
```
