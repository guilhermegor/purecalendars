# **API Reference**

Complete public interface for `purecalendars`.

> **See also:** [Usage](../usage.md)

The public API is the set of **country providers**, one class per module under a two-letter
country package (`purecalendars.<country>.<provider>`). Every provider **loads a different holiday
calendar** but **shares the same date-operations surface** — the [shared calendar
operations](#shared-calendar-operations) documented at the bottom of this page.

Every provider is computed **offline** — no network, no cache. Live fetchers of the publishers'
own tables live in the separate `opendata-calendars` package.

| Provider | Import | Holidays it loads |
|----------|--------|-------------------|
| [`DatesBRAnbima`](#datesbranbima) | `purecalendars.br.anbima` | Brazilian **national** holidays (ANBIMA) |
| [`DatesBRFebraban`](#datesbrfebraban) | `purecalendars.br.febraban` | Brazilian **bank** holidays (FEBRABAN) |
| [`DatesBRB3`](#datesbrb3) | `purecalendars.br.b3` | National **+ B3 exchange** non-trading days |
| [`DatesUSFederalHolidays`](#datesusfederalholidays) | `purecalendars.us.federal_holidays` | US **federal** public holidays |

### Constructor parameters

Every provider computes its holidays locally, so the constructors take only `int_year_start`,
`int_year_end`, and an optional `logger` (plus `bool_add_christmas_eve` for `DatesBRB3`).

---

## Brazil — `purecalendars.br`

!!! info "Why the offline BR calendars use `holidays.B3`"
    The offline Brazilian providers are computed from `holidays.B3` (Brasil, Bolsa, Balcão),
    **not** `holidays.Brazil`. The latter is the statutory-only national set and omits
    **Carnaval** (Monday and Tuesday) and **Corpus Christi** — neither is a statutory national
    holiday, but banks and markets close on both. Using it would silently mark Carnaval as a
    working day.

    The equivalence was verified before the default was switched: over the full **2001–2099**
    span ANBIMA publishes, the offline set and the fetched workbook have an **empty symmetric
    difference**. The same holds for FEBRABAN (checked against its live endpoint for 2025–2026)
    and for B3 once its last-working-day-of-year rule is applied.

### `DatesBRAnbima`

The ANBIMA calendar — computed **offline**, no network.

```python
from purecalendars.br.anbima import DatesBRAnbima

DatesBRAnbima(
    int_year_start=2001, int_year_end=2099,   # defaults: ANBIMA's full published span
    logger=None,
)
```

**Holidays:** the Brazilian **national** holiday set published by ANBIMA — Confraternização
Universal (New Year), Carnaval, Sexta-feira Santa (Good Friday), Tiradentes, Dia do Trabalho,
Corpus Christi, Independência, Nossa Senhora Aparecida, Finados, Proclamação da República,
Consciência Negra, Natal.

**Source:** the [`holidays`](https://pypi.org/project/holidays/) package (offline computation).
**No cache parameters** — there is nothing to fetch.

**Provider-specific methods:** none beyond the [shared surface](#shared-calendar-operations);
`holidays()` returns the computed `(name, date)` list.

### `DatesBRFebraban`

The FEBRABAN calendar — computed **offline**, no network.

```python
from purecalendars.br.febraban import DatesBRFebraban

DatesBRFebraban(
    int_year_start=2025, int_year_end=2026,   # defaults: last year and this year
    logger=None,
)
```

**Holidays:** Brazilian **bank** holidays (bank non-working days) for the requested
`int_year_start`…`int_year_end` range.

**Source:** the `holidays` package (offline computation). FEBRABAN has no dedicated entry in
that package, but its published federal bank holidays were verified identical to `holidays.B3`
for 2025 and 2026; years outside that window follow the same statutory rules but have not been
diffed against FEBRABAN's own publication.

**Provider-specific methods:** none beyond the [shared surface](#shared-calendar-operations).

### `DatesBRB3`

The B3 calendar — computed **offline**, no network.

```python
from purecalendars.br.b3 import DatesBRB3

DatesBRB3(
    bool_add_christmas_eve=True,              # 24 Dec is a non-trading day (default)
    int_year_start=2001, int_year_end=2099,
    logger=None,
)
```

**Holidays:** the **national** set **plus** the B3 exchange's own non-trading days — the last
working day of each year, and **24 December** (Christmas Eve). Use this provider for
**trading-day** logic on the Brazilian exchange.

`bool_add_christmas_eve` **defaults to `True`** because B3's published calendar carries 24 December
as a closure (*"não haverá negociação"*) in every year it falls on a weekday — verified live for
2021, 2024, 2025 and 2026. Pass `False` to restore the pre-2.0 behaviour, in which the offline
calendar omitted the date and therefore disagreed with the exchange.

!!! note "Changed in 2.0"
    The default was `False` up to and including 1.0.1, so `DatesBRB3()` used to report 24 December
    as a **working** day. If you depend on that, pass `bool_add_christmas_eve=False` explicitly.
    The date is added unconditionally, so in a year where 24 December falls on a weekend it appears
    in the holiday list even though B3 omits it — harmless for working-day arithmetic, since a
    weekend is already non-working.

**Source:** the `holidays` package + B3 exchange rules (offline computation).

**Provider-specific methods:**

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `holidays_to_add` | `(set_dates_national)` | `list[tuple[str, date]]` | The extra `(name, date)` pairs B3 adds beyond the national set. |
| `get_last_working_day` | `(int_year, set_dates_national)` | `date` | The year's last non-weekend, non-holiday day. |
| `get_christmas_eve` | `(int_year)` | `date` | 24 December of `int_year` (added unless `bool_add_christmas_eve=False`). |

## United States — `purecalendars.us`

### `DatesUSFederalHolidays`

The US federal calendar — computed **offline**, no network and no
browser.

```python
from purecalendars.us.federal_holidays import DatesUSFederalHolidays

DatesUSFederalHolidays(
    int_year_start=2024, int_year_end=2025,   # year range to compute
    logger=None,
)
```

**Holidays:** the eleven US **federal** public holidays for the requested year range (New
Year's, MLK, Washington's Birthday, Memorial, Juneteenth, Independence, Labor, Columbus,
Veterans, Thanksgiving, Christmas), computed from their statutory rules via the
[`holidays`](https://pypi.org/project/holidays/) package.

**Observed-day rule (5 U.S.C. §6103).** When a holiday falls on a weekend, the observed federal
closure day is **also** emitted: a Saturday holiday is observed the preceding Friday, a Sunday
holiday the following Monday. Both the statutory date **and** the observed date are returned —
e.g. for 2023, New Year's Day appears on **Sunday 1 Jan** *and* the observed closure on
**Monday 2 Jan**. Nothing is hidden or moved; the Monday is added because federal offices,
banks, and markets are genuinely closed then, which is required for correct working-day math.

**Source:** the `holidays` package (offline computation). **No cache parameters** — there is
nothing to fetch, so the constructor takes only the year range and an optional logger.

**Provider-specific methods:** none beyond the [shared surface](#shared-calendar-operations);
`holidays()` returns the computed `(name, date)` list.

## Shared calendar operations

**Every provider inherits all of the methods below** — they are canonical to each calendar
class. They come from a linear chain of internal capability mixins that build up the
`ABCCalendarOperations` facade every provider extends:

```
ABCCalendar → CalendarCore → DateManipulation → DateTimezoneAware
            → DatesRangeDelta → DatesCurrent → DateFormatter → ABCCalendarOperations
```

Each layer below lists the methods it contributes. Throughout, `date_` accepts either a
`date` or a `datetime`.

### Holidays & working-day predicates — `CalendarCore`

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `holidays` | `()` | `list[tuple[str, date]]` | Every holiday the provider loads, as `(name, date)` pairs — the base set all working-day logic builds on. |
| `holidays_in_year` | `(int_year)` | `list[int]` | Day-of-year ordinals that fall on a holiday in `int_year`; handy for fast membership checks. |
| `is_holiday` | `(date_)` | `bool` | Whether the date is a loaded holiday. Gate settlement / trading logic on this. |
| `is_weekend` | `(date_)` | `bool` | Whether the date is a Saturday or Sunday. |
| `is_working_day` | `(date_)` | `bool` | The core business-day test — `True` when the date is neither weekend nor holiday. |
| `date_only` | `(date_)` | `date` | Normalise a `datetime` to its `date`, dropping the time; used before day arithmetic. |
| `get_holidays_raw` | `(timeout=(12.0, 21.0))` | `DataFrame` | The untransformed upstream holiday table — for debugging or custom pipelines. |

### Date manipulation — `DateManipulation`

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `add_holidays` | `(list_new_holidays)` | `None` | Inject extra `(name, date)` holidays at runtime — e.g. a one-off company closure on top of the official set. |
| `add_working_days` | `(date_, int_days_to_add)` | `date` | Advance by N business days, skipping weekends + holidays (negative N goes back). The T+N settlement primitive. |
| `add_calendar_days` | `(date_, int_days_to_add)` | `date` | Add N calendar days, ignoring weekends/holidays. |
| `add_months` | `(date_, int_months_to_add)` | `datetime` | Add N calendar months, preserving day-of-month where valid. |
| `nearest_working_day` | `(date_, bool_next=True)` | `date` | Snap a date to the nearest business day — forward by default, backward with `bool_next=False`. Rolls a due date off a holiday. |
| `build_date` | `(year, month, day)` | `date` | Construct a `date` from components. |
| `build_datetime` | `(year, month, day, hour, minute, second, str_timezone="UTC")` | `datetime` | Construct a timezone-aware `datetime` from components. |
| `str_date_to_date` | `(str_date, format_input="DD/MM/YYYY")` | `date` | Parse a date string using a format token (e.g. `"YYYY-MM-DD"`) into a `date`. |
| `timestamp_to_date` | `(timestamp_, substr_timestamp="T")` | `date` | Parse a timestamp string into a `date`, splitting on `substr_timestamp`. |
| `timestamp_to_datetime` | `(timestamp_, substr_timestamp="T")` | `datetime` | Parse a timestamp string into a `datetime`. |
| `excel_float_to_date` | `(numeric_excel_date)` | `date` | Convert an Excel serial number to a `date` (handles the 1900 leap-year bug). |
| `to_integer` | `(date_)` | `int` | Encode a date as a `YYYYMMDD` integer — a compact sortable key for storage/comparison. |

### Timezone & timestamp conversion — `DateTimezoneAware`

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `change_timezone` | `(date_, target_tz="UTC", source_tz=None)` | `datetime` | Re-express a date/datetime in `target_tz`; pass `source_tz` for naive inputs. |
| `date_to_datetime` | `(date_, str_timezone="UTC")` | `datetime` | Promote a `date` to a midnight `datetime` in the given timezone. |
| `str_date_to_datetime` | `(str_date, format_input="DD/MM/YYYY", str_timezone="UTC")` | `datetime` | Parse a date string to a timezone-aware `datetime`. |
| `to_unix_timestamp` | `(date_, str_timezone="UTC")` | `int` | Convert a date / datetime / time to Unix epoch seconds. |
| `iso_to_unix_timestamp` | `(iso_timestamp, str_timezone="UTC")` | `int` | Convert an ISO-8601 string to Unix epoch seconds. |
| `unix_timestamp_to_date` | `(unix_timestamp, str_timezone="UTC")` | `date` | Convert Unix epoch seconds back to a `date` in the given timezone. |
| `unix_timestamp_to_datetime` | `(unix_timestamp, str_timezone="UTC")` | `datetime` | Convert Unix epoch seconds back to a `datetime`. |
| `excel_float_to_datetime` | `(float_date, str_timezone="UTC")` | `datetime` | Convert an Excel serial number to a timezone-aware `datetime`, including the fractional-day time. |

### Ranges & deltas — `DatesRangeDelta`

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `working_days_range` | `(date_start, date_end)` | `set[date]` | All business days within `[start, end]` inclusive. |
| `calendar_days_range` | `(date_start, date_end)` | `set[date]` | All calendar days within `[start, end]` inclusive. |
| `delta_working_days` | `(date_start, date_end)` | `int` | Count of business days between two dates — e.g. SLA / aging in business days. |
| `delta_calendar_days` | `(date_start, date_end)` | `int` | Count of calendar days between two dates. |
| `delta_working_hours` | `(timestamp_start, timestamp_end, …office/lunch hours…)` | `int` | Business hours between two timestamps, honouring configurable office + lunch windows and holidays. |
| `get_dates_weekday_month` | `(year, month, weekday)` | `list[date]` | Every occurrence of a given weekday in a month (e.g. all Mondays). |
| `get_last_working_day_years` | `(list_years)` | `list[date]` | The last business day of each requested year — for year-end processing. |
| `get_nth_weekday_month` | `(year, month, weekday, n, bool_working_days=True, bool_next_working_day=True)` | `date` | The n-th given weekday of a month (e.g. 3rd Wednesday — options expiry), optionally rolled to a working day. |
| `get_start_end_day_month` | `(date_, bool_working_days=False)` | `tuple[date, date]` | The first and last day of a date's month, optionally as working days. |
| `years_between_dates` | `(date_start, date_end)` | `set[int]` | The set of calendar years a range spans. |

### Current date & time — `DatesCurrent`

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `curr_date` | `()` | `date` | Today's date. |
| `curr_datetime` | `(str_timezone="UTC")` | `datetime` | The current datetime in the given timezone. |
| `curr_time` | `(str_timezone="UTC")` | `time` | The current time-of-day in the given timezone. |
| `current_timestamp_string` | `(format_output="%Y%m%d_%H%M%S", str_timezone="UTC")` | `str` | The current timestamp formatted as a string — handy for filenames / log keys. |

### Formatting & components — `DateFormatter`

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `day_number` | `(date_)` | `int` | Day of month (1–31). |
| `week_number` | `(date_)` | `str` | ISO week number. |
| `month_number` | `(date_, bool_month_mm=False)` | `int \| str` | Month as an `int`, or a zero-padded `"MM"` string when `bool_month_mm=True`. |
| `month_name` | `(date_, bool_abbreviation=False, str_timezone="UTC")` | `str` | Locale-aware month name (full, or abbreviated when `bool_abbreviation=True`). |
| `month_str` | `(date_)` | `str` | Month rendered as a string. |
| `year_number` | `(date_)` | `int` | Four-digit year. |
| `weekday_name` | `(date_, bool_abbreviation=False, str_timezone="UTC")` | `str` | Locale-aware weekday name (full, or abbreviated when `bool_abbreviation=True`). |
| `get_platform_locale` | `(str_locale=None, str_timezone=None)` | `str` | Resolve a platform-appropriate locale string backing the name methods above. |
| `utc_log_ts` | `()` | `datetime` | A UTC datetime intended for log timestamps. |

### Subclassing `ABCCalendarOperations`

`ABCCalendarOperations` is public: `from purecalendars import ABCCalendarOperations`. Subclass it
to build a calendar of your own and inherit every method above.

**Override to supply holidays.** `_source_holidays(self) -> list[tuple[str, date]]` — the
`(name, date)` pairs of your calendar. Its default returns `[]` and nothing is abstract, so a
subclass that omits or misspells it raises nothing and has weekends as its only non-working days.

**May override.** `get_holidays_raw(timeout)` — returns an empty `DataFrame` (`name`, `date`
columns) by default; override it to expose an upstream table.

**Should not override.** `holidays()` — it returns `_source_holidays()` plus the holidays added
through `add_holidays`, so overriding it drops those additions.

**May rely on.**

- `holidays()` and the whole surface (`is_holiday`, `is_working_day`, `add_working_days`, ...)
  reading the calendar through `_source_holidays`; weekends are non-working on top of it.
- `add_holidays` working even when your `__init__` does not call `super().__init__()`.

**Must not assume.** That `_source_holidays` is re-read on every call: the date set behind
`is_holiday` and `is_working_day` is built on first use and refreshed only by `add_holidays`, so
fix your configuration (for example a year range) before the first query.

```python
from datetime import date

from purecalendars import ABCCalendarOperations


class DatesXX(ABCCalendarOperations):
    def _source_holidays(self) -> list[tuple[str, date]]:
        return [("New Year", date(2026, 1, 1))]
```

---

## Conventions

| Convention | Rule |
|------------|------|
| Public API | `ABCCalendarOperations` from the package root; country providers under `purecalendars.<cc>.<provider>`, one class per module. |
| Private code | Everything under `purecalendars._internal` is off-limits — internal, may change. |
| Type hints | Required on all public methods, including `-> None` returns. |
| Docstrings | NumPy style; explain *why*, not *what*. |
