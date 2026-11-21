"""Pin the package-root public API."""

from datetime import date

import pytest

import purecalendars
from purecalendars import ABCCalendarOperations
from purecalendars._internal.utils.calendars import abc_calendar_operations


def test_abc_calendar_operations_importable_from_root() -> None:
    """The base class is importable from the package root."""
    from purecalendars import ABCCalendarOperations  # noqa: F401, PLC0415


def test_abc_calendar_operations_in_all() -> None:
    """The base class is listed in ``__all__``."""
    assert "ABCCalendarOperations" in purecalendars.__all__


def test_abc_calendar_operations_is_internal_object() -> None:
    """The root export is the very class defined in the internal module."""
    assert purecalendars.ABCCalendarOperations is abc_calendar_operations.ABCCalendarOperations


class _DatesEmpty(ABCCalendarOperations):
    """Subclass overriding nothing."""


class _DatesXX(ABCCalendarOperations):
    """Subclass whose ``__init__`` deliberately skips ``super().__init__()``."""

    def __init__(self) -> None:
        self.str_marker = "xx"

    def _source_holidays(self) -> list[tuple[str, date]]:  # noqa: PLR6301
        return [("New Year", date(2026, 1, 1))]


def test_empty_subclass_instantiates_with_no_holidays() -> None:
    """A subclass overriding nothing instantiates and has no holidays."""
    assert _DatesEmpty().holidays() == []


@pytest.mark.parametrize(
    "dt_day",
    [date(2026, 1, 1), date(2026, 1, 3), date(2026, 1, 4)],
    ids=["source-holiday", "saturday", "sunday"],
)
def test_subclass_holiday_and_weekend_are_not_working_days(dt_day: date) -> None:
    """The subclass's own holiday and both weekend days are non-working."""
    assert not _DatesXX().is_working_day(dt_day)


def test_add_holidays_refreshes_cache_without_super_init() -> None:
    """``add_holidays`` after first use applies, on a subclass that skips ``super().__init__``."""
    cls_calendar = _DatesXX()
    cls_calendar.is_working_day(date(2026, 1, 2))
    cls_calendar.add_holidays([("Bridge", date(2026, 1, 2))])
    assert not cls_calendar.is_working_day(date(2026, 1, 2))
