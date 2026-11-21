# Ledger — #110 public-calendar-base

Branch: `feat/110-public-calendar-base` · Issue: #110 · Class: **src**

## Goal

Expose `ABCCalendarOperations` as public API so `opendata-calendars` can subclass it without
reaching into `_internal`.

## Work

- [x] Re-export `ABCCalendarOperations` from `purecalendars` and list it in `__all__`
- [x] Document the subclass contract in the class docstring and `docs/api/reference.md`
- [x] Pin the public name in `tests/unit/test_public_api.py`
- [x] Mention it in the README Public API section
- [x] Pin the documented subclass contract (empty subclass, weekends, `add_holidays`
      refresh without `super().__init__()`) after the fallback review

## Not done, on purpose

- The 4.1.0 release: cut separately, not part of this PR.

Completed — kept as a record.
