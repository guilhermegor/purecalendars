"""Introspective convention test for the public calendar-provider family.

The providers are discovered from ``purecalendars.br.__all__`` and ``purecalendars.us.__all__``,
never hand-listed, so a new provider that skips the convention fails here without anyone
editing this file. The convention: a provider extends ``ABCCalendarOperations`` and is built
from an ``int_year_start`` / ``int_year_end`` range.
"""

import inspect

import pytest

from purecalendars import br, us
from purecalendars._internal.utils.calendars.abc_calendar_operations import ABCCalendarOperations


_FAMILY = tuple(
    cls_member
    for module in (br, us)
    for cls_member in (getattr(module, str_name) for str_name in module.__all__)
    if inspect.isclass(cls_member)
)


def test_the_discovered_family_is_not_empty() -> None:
    """Guard the discovery itself: an empty family makes every per-member test vacuous."""
    assert _FAMILY, "no provider discovered from the public surface"


def test_discovery_matches_declared_surface() -> None:
    """Every name declared in ``__all__`` of ``br`` and ``us`` resolved to a class."""
    assert len(_FAMILY) == len(br.__all__) + len(us.__all__)


@pytest.mark.parametrize("cls_member", _FAMILY, ids=lambda cls: cls.__name__)
def test_member_extends_the_calendar_base(cls_member: type) -> None:
    """Assert each provider extends ``ABCCalendarOperations``.

    Parameters
    ----------
    cls_member : type
            A provider discovered from the public surface.
    """
    assert issubclass(cls_member, ABCCalendarOperations)


@pytest.mark.parametrize("cls_member", _FAMILY, ids=lambda cls: cls.__name__)
def test_member_takes_a_year_range(cls_member: type) -> None:
    """Assert each provider's constructor accepts the shared year-range arguments.

    Parameters
    ----------
    cls_member : type
            A provider discovered from the public surface.
    """
    set_params = set(inspect.signature(cls_member.__init__).parameters)
    assert {"int_year_start", "int_year_end"} <= set_params
