"""Pin the package-root public API."""

import purecalendars
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
