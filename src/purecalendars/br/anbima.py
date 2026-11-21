"""ANBIMA Brazilian holiday calendar — offline, computed via the ``holidays`` package.

No network and no cache: the ANBIMA national holiday table is reproduced from
``holidays.B3``, which was verified identical to the published
``feriados_nacionais.xls`` across all 2001–2099 years it covers.

For the table fetched live from anbima.com.br, use the ``opendata-calendars`` package.
"""

from datetime import date
from logging import Logger

from purecalendars.br._offline_holidays import (
    _INT_YEAR_END_DEFAULT,
    _INT_YEAR_START_DEFAULT,
    _national_holidays,
)
from purecalendars.calendar_operations import ABCCalendarOperations


class DatesBRAnbima(ABCCalendarOperations):
    """ANBIMA Brazilian national holiday calendar computed offline.

    References
    ----------
    .. [1] https://www.anbima.com.br/feriados/arqs/feriados_nacionais.xls
    """

    def __init__(
        self,
        int_year_start: int = _INT_YEAR_START_DEFAULT,
        int_year_end: int = _INT_YEAR_END_DEFAULT,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the offline ANBIMA holiday calendar.

        Parameters
        ----------
        int_year_start : int
            First year to include (default: 2001, ANBIMA's first published year).
        int_year_end : int
            Last year to include (default: 2099, ANBIMA's last published year).
        logger : Optional[Logger]
            Logger object for logging (default: None).

        Returns
        -------
        None
        """
        self.int_year_start = int_year_start
        self.int_year_end = int_year_end
        self._logger = logger

    def _source_holidays(self) -> list[tuple[str, date]]:
        """Return the ANBIMA national holidays for the configured year range.

        Returns
        -------
        list[tuple[str, date]]
            Tuples of ``(name, date)``, sorted by date.
        """
        return _national_holidays(self.int_year_start, self.int_year_end)
