"""DateFormatter-derived — calendar mixin."""

from purecalendars._internal.utils.calendars._date_formatter import DateFormatter


class ABCCalendarOperations(DateFormatter):
    """Base class of every calendar provider; public so third parties can subclass it.

    Exported as ``purecalendars.ABCCalendarOperations``. It carries the whole business-day
    surface (working-day predicates, arithmetic, ranges and deltas, timezone and formatting
    helpers) on top of a holiday list the subclass supplies.

    Subclass contract
    -----------------
    Nothing is left abstract: the abstract ``holidays`` and ``get_holidays_raw`` of the
    internal ``ABCCalendar`` root are already implemented further down the chain, so an
    empty subclass instantiates and simply has no holidays.

    * **Override to supply holidays:** ``_source_holidays(self) -> list[tuple[str, date]]``,
      the ``(name, date)`` pairs of the provider's own calendar. This is the single extension
      point every bundled provider overrides. Its default returns ``[]``, so a subclass that
      omits or misspells it raises nothing and has weekends as its only non-working days.
    * **May override:** ``get_holidays_raw(timeout)``, which defaults to an empty
      ``DataFrame`` with ``name`` and ``date`` columns, for providers that expose an
      upstream table.
    * **Should not override:** ``holidays()``. It returns ``_source_holidays()`` plus the
      holidays injected through ``add_holidays``, so overriding it drops those additions.

    A subclass may rely on:

    * ``holidays()``, ``is_holiday``, ``is_working_day``, ``add_working_days`` and the
      rest of the surface reading the calendar through ``_source_holidays``.
    * ``add_holidays`` working on any subclass, even one whose ``__init__`` does not
      call ``super().__init__()``.
    * Weekends (Saturday and Sunday) being non-working in addition to the holidays.

    A subclass must not assume that ``_source_holidays`` is re-read on every call: the set
    of holiday dates behind ``is_holiday`` and ``is_working_day`` is built on first use and
    is refreshed only by ``add_holidays``. Fix the provider's configuration, such as its
    year range, before the first query.

    Examples
    --------
    >>> from datetime import date
    >>> from purecalendars import ABCCalendarOperations
    >>> class DatesXX(ABCCalendarOperations):
    ...     def _source_holidays(self) -> list[tuple[str, date]]:
    ...         return [("New Year", date(2026, 1, 1))]
    >>> DatesXX().is_working_day(date(2026, 1, 1))
    False
    """
