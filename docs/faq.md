# **FAQ & Troubleshooting**

Common questions and fixes when using `purecalendars`.

> **See also:** [Usage](usage.md) · [API Reference](api.md)

---

## Where did `DatesBRB3Web`, `DatesUSNasdaq` and the other live fetchers go?

They moved to the separate `opendata-calendars` package when `wwdates` became `purecalendars`
(3.0.0). `purecalendars` does no I/O: every provider here is computed offline, with no network,
no cache and no browser. `opendata-calendars` fetches the publishers' live tables and returns
them as `purecalendars` calendars.

## Why does a US federal holiday show up on both a Sunday *and* the next Monday?

That is correct and intentional. `DatesUSFederalHolidays` follows the federal observed-day rule
(5 U.S.C. §6103): when a holiday lands on a weekend, the observed closure day is emitted **in
addition** to the statutory date — a Saturday holiday is observed the preceding Friday, a Sunday
holiday the following Monday. So for 2023, New Year's Day appears on **Sun 1 Jan** (statutory)
*and* **Mon 2 Jan** (observed). Nothing is moved or hidden; the Monday is added because federal
offices, banks, and markets are genuinely closed then — and `is_working_day(Mon 2 Jan)` must
return `False` for correct business-day math. Brazilian calendars have no such rule and keep
each holiday on its published date.

---

## Can a holiday be stale?

Not in the cache sense: every provider recomputes from statutory rules on every call, so there
is nothing to refresh. A calendar can only be wrong when a publisher declares an extraordinary
closure the rules do not know; add it yourself (see below) until a release picks it up.

---

## `ZoneInfoNotFoundError` on a timezone lookup

`purecalendars` depends on `tzdata` so the IANA timezone database is available even on systems that
ship none (notably Windows and minimal containers). If you see this error, confirm `tzdata`
installed alongside the package:

```bash
pip show tzdata
```

---

## Which provider should I use for trading-day logic?

- **Brazilian exchange (B3):** `DatesBRB3` — national holidays plus B3 non-trading days,
  **including 24 December**, which B3 publishes as a closure (pass
  `bool_add_christmas_eve=False` to opt out; the default changed in 2.0).
- **Brazilian banking / settlement:** `DatesBRFebraban`.
- **US market:** `DatesUSFederalHolidays` is the civil federal-holiday calendar, not the
  exchange's. Nasdaq market closures (e.g. Good Friday) come from `opendata-calendars`.

See the [provider comparison table](api.md) for what each one loads.

---

## Can I add my own one-off holidays?

Yes — every provider inherits `add_holidays`:

```python
from datetime import date
from purecalendars.br.b3 import DatesBRB3

cls_cal = DatesBRB3()
cls_cal.add_holidays([("Company offsite", date(2025, 6, 2))])
```
