"""Brazilian holiday calendars (ANBIMA, FEBRABAN, B3).

Every provider is computed offline from the ``holidays`` package — no network, no cache. The
tables were verified against each publisher's live page; see
:mod:`purecalendars.br._offline_holidays`. Live fetchers live in ``opendata-calendars``.
"""

from purecalendars.br.anbima import DatesBRAnbima
from purecalendars.br.b3 import DatesBRB3
from purecalendars.br.febraban import DatesBRFebraban


__all__ = ["DatesBRAnbima", "DatesBRB3", "DatesBRFebraban"]
