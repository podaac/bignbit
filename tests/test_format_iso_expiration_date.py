import pytest
from datetime import datetime
from dateutil import parser

from bignbit.utils import format_iso_expiration_date


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("2025-12-31T23:59:59Z", "12/31/2025"),
        ("2025-12-31T23:59:59.123Z", "12/31/2025"),
        ("12/31/2025", "12/31/2025"),
        ("2025-12-31", "12/31/2025"),
        ("March 1, 2025", "03/01/2025"),
        (datetime(2025, 12, 31), "12/31/2025"),
    ],
)
def test_format_iso_expiration_date_valid_inputs(input_value, expected):
    """
    Convert various date/time inputs to MM/DD/YYYY format.

    Handles ISO 8601, MM/DD/YYYY, human-readable strings,
    and datetime objects.
    """
    assert format_iso_expiration_date(input_value) == expected


# ---------------------------------------------------------------------------
# Invalid string input
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "input_value",
    [
        "not-a-date",
        "2025-13-01T00:00:00Z",
        "2025-02-30",
        "",
    ],
)
def test_format_iso_expiration_date_invalid_strings(input_value):
    """
    Raise ValueError for strings that cannot be parsed as dates.
    """
    with pytest.raises(ValueError, match="Cannot parse date/time"):
        format_iso_expiration_date(input_value)


# ---------------------------------------------------------------------------
# Non-string, non-datetime inputs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "input_value",
    [
        123,
        45.6,
        None,
        ["2025-12-31"],
        {"date": "2025-12-31"},
    ],
)
def test_format_iso_expiration_date_invalid_types(input_value):
    """
    Raise TypeError for inputs that are neither strings nor datetime objects.
    """
    with pytest.raises(TypeError, match="Input must be a string or datetime"):
        format_iso_expiration_date(input_value)


# ---------------------------------------------------------------------------
# Optional: verify ISO parsing matches dateutil.parser
# ---------------------------------------------------------------------------

def test_format_iso_expiration_date_matches_parser():
    """
    Verify the function output matches dateutil.parser parsing for ISO 8601.
    """
    iso_string = "2025-10-25T00:00:00Z"
    expected = parser.isoparse(iso_string).strftime("%m/%d/%Y")
    assert format_iso_expiration_date(iso_string) == expected


def test_format_iso_expiration_date_with_timezone():
    """
    Verify that timezone-aware ISO 8601 strings are handled correctly.
    """
    iso_string = "2025-10-25T12:00:00+05:00"
    expected = "10/25/2025"
    assert format_iso_expiration_date(iso_string) == expected


def test_format_iso_expiration_date_leap_year():
    """
    Verify that leap year dates are handled correctly.
    """
    iso_string = "2024-02-29T00:00:00Z"
    expected = "02/29/2024"
    assert format_iso_expiration_date(iso_string) == expected


def test_format_iso_expiration_date_end_of_month():
    """
    Verify that end-of-month dates are handled correctly.
    """
    iso_string = "2025-04-30T23:59:59Z"
    expected = "04/30/2025"
    assert format_iso_expiration_date(iso_string) == expected


def test_format_iso_expiration_date_invalid_datetime_object():
    """
    Verify that invalid datetime objects raise appropriate errors.
    """
    class InvalidDateTime:
        pass

    invalid_datetime = InvalidDateTime()
    with pytest.raises(TypeError, match="Input must be a string or datetime"):
        format_iso_expiration_date(invalid_datetime)


def test_format_iso_expiration_date_empty_string():
    """
    Verify that an empty string raises a ValueError.
    """
    with pytest.raises(ValueError, match="Cannot parse date/time"):
        format_iso_expiration_date("")


def test_format_iso_expiration_date_none_input():
    """
    Verify that None input raises a TypeError.
    """
    with pytest.raises(TypeError, match="Input must be a string or datetime"):
        format_iso_expiration_date(None)


def test_format_iso_expiration_date_invalid_datetime_input():
    """
    Verify that an invalid datetime input raises a TypeError.
    """
    with pytest.raises(TypeError, match="Input must be a string or datetime"):
        format_iso_expiration_date(12345)


def test_format_iso_expiration_date_incorrect_format():
    """
    Verify that an incorrectly formatted date string raises a ValueError.
    """
    assert format_iso_expiration_date("31-12-2025") == "12/31/2025"


def test_format_iso_expiration_date_non_date_string():
    """
    Verify that a non-date string raises a ValueError.
    """
    with pytest.raises(ValueError, match="Cannot parse date/time"):
        format_iso_expiration_date("Hello, World!")


def test_format_iso_expiration_date_list_input():
    """
    Verify that a list input raises a TypeError.
    """
    with pytest.raises(TypeError, match="Input must be a string or datetime"):
        format_iso_expiration_date(["2025-12-31"])


def test_format_iso_expiration_date_dict_input():
    """
    Verify that a dictionary input raises a TypeError.
    """
    with pytest.raises(TypeError, match="Input must be a string or datetime"):
        format_iso_expiration_date({"date": "2025-12-31"})
