"""Unit tests for the offline US federal holiday calendar."""

from datetime import date

import pytest

from purecalendars.us import DatesUSFederalHolidays


# --------------------------
# Tests for DatesUSFederalHolidays (offline, holidays package)
# --------------------------
def test_federal_offline_init_valid() -> None:
    """Test initialization of the offline DatesUSFederalHolidays.

    Verifies
    --------
    - Year range is stored
    - No cache manager is created (the offline calendar needs no cache)

    Returns
    -------
    None
    """
    instance = DatesUSFederalHolidays(int_year_start=2024, int_year_end=2025)
    assert instance.int_year_start == 2024
    assert instance.int_year_end == 2025
    assert not hasattr(instance, "cls_cache_manager")


def test_federal_offline_holidays_emit_statutory_and_observed() -> None:
    """Test that a weekend holiday emits both statutory and observed dates.

    1 January 2023 fell on a Sunday, so both that Sunday (statutory) and the following
    Monday (observed, per 5 U.S.C. §6103) must be present.

    Returns
    -------
    None
    """
    instance = DatesUSFederalHolidays(int_year_start=2023, int_year_end=2023)
    set_dates = {day for _, day in instance.holidays()}
    assert date(2023, 1, 1) in set_dates  # statutory New Year (Sunday)
    assert date(2023, 1, 2) in set_dates  # observed closure (Monday)
    assert instance.is_holiday(date(2023, 1, 1)) is True
    assert instance.is_working_day(date(2023, 1, 2)) is False


def test_federal_offline_holidays_offline_no_network() -> None:
    """Test that the offline calendar returns a non-empty (name, date) list.

    Returns
    -------
    None
    """
    result = DatesUSFederalHolidays(int_year_start=2025, int_year_end=2025).holidays()
    assert isinstance(result, list)
    assert result
    assert all(isinstance(name, str) and isinstance(day, date) for name, day in result)


def test_federal_offline_invalid_year_range() -> None:
    """Test that an inverted year range raises ValueError.

    Returns
    -------
    None
    """
    instance = DatesUSFederalHolidays(int_year_start=2026, int_year_end=2025)
    with pytest.raises(ValueError, match="Start year must be less than or equal to end year"):
        instance.holidays()
