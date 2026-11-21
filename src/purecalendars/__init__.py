"""purecalendars — holiday calendars and business-day arithmetic, computed offline.

Import the country subpackages for the concrete providers, e.g.
``from purecalendars.br import DatesBRB3`` or
``from purecalendars.us import DatesUSFederalHolidays``.
Live calendars fetched from their publishers live in the separate ``opendata-calendars`` package.
"""

from importlib.metadata import PackageNotFoundError, version

from purecalendars.calendar_operations import ABCCalendarOperations


try:
    __version__ = version("purecalendars")
except PackageNotFoundError:  # pragma: no cover - source tree without an installed dist
    __version__ = "0.0.0"


__all__ = ["ABCCalendarOperations", "__version__"]
