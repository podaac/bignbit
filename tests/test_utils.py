import os
import json
import pathlib
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest
from dateutil import parser

from bignbit.utils import (
    format_iso_expiration_date,
    sha512sum,
    extract_mgrs_grid_code,
    CustomDateTimeEncoder,
    json_dumps_with_datetime,
    extract_granule_dates,
    parse_datetime,
    parse_doy,
    get_harmony_client,
    Environment
)


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
        format_iso_expiration_date(invalid_datetime) # type: ignore


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
        format_iso_expiration_date(None) # type: ignore


def test_format_iso_expiration_date_invalid_datetime_input():
    """
    Verify that an invalid datetime input raises a TypeError.
    """
    with pytest.raises(TypeError, match="Input must be a string or datetime"):
        format_iso_expiration_date(12345) # type: ignore


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
        format_iso_expiration_date(["2025-12-31"]) # type: ignore


def test_format_iso_expiration_date_dict_input():
    """
    Verify that a dictionary input raises a TypeError.
    """
    with pytest.raises(TypeError, match="Input must be a string or datetime"):
        format_iso_expiration_date({"date": "2025-12-31"}) # type: ignore


# ---------------------------------------------------------------------------
# Tests for sha512sum()
# ---------------------------------------------------------------------------

def test_sha512sum():
    """Test SHA512 hash generation for a file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        temp_path = pathlib.Path(f.name)

    try:
        result = sha512sum(temp_path)
        # Just verify it's a valid SHA512 hash (128 hex chars)
        assert len(result) == 128
        assert all(c in '0123456789abcdef' for c in result)
    finally:
        temp_path.unlink()


def test_sha512sum_empty_file():
    """Test SHA512 hash generation for an empty file."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = pathlib.Path(f.name)

    try:
        result = sha512sum(temp_path)
        # SHA512 hash of empty content
        expected = "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce" \
                   "47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
        assert result == expected
    finally:
        temp_path.unlink()


def test_sha512sum_large_file():
    """Test SHA512 hash generation for a larger file."""
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        # Write 1MB of data
        f.write(b'a' * (1024 * 1024))
        temp_path = pathlib.Path(f.name)

    try:
        result = sha512sum(temp_path)
        assert len(result) == 128
        assert all(c in '0123456789abcdef' for c in result)
    finally:
        temp_path.unlink()


# ---------------------------------------------------------------------------
# Tests for extract_mgrs_grid_code()
# ---------------------------------------------------------------------------

def test_extract_mgrs_grid_code_from_additional_attributes():
    """Test extracting MGRS grid code from AdditionalAttributes."""
    umm_json = {
        'GranuleUR': 'test_granule',
        'AdditionalAttributes': [
            {'Name': 'SOME_OTHER_ATTR', 'Values': ['value1']},
            {'Name': 'MGRS_TILE_ID', 'Values': ['T32VMJ']}
        ]
    }
    result = extract_mgrs_grid_code(umm_json)
    assert result == 'T32VMJ'


def test_extract_mgrs_grid_code_from_granule_id_position_3():
    """Test extracting MGRS grid code from GranuleUR at position 3."""
    umm_json = {
        'GranuleUR': 'OPERA_L3_DSWx-HLS_T48SUE_20190302T034350Z_20230131T222341Z_L8_30_v0.0'
    }
    result = extract_mgrs_grid_code(umm_json)
    assert result == 'T48SUE'


def test_extract_mgrs_grid_code_from_granule_id_pattern_match():
    """Test extracting MGRS grid code from GranuleUR via regex pattern."""
    umm_json = {
        'GranuleUR': 'OPERA_L3_DSWx-HLS_some_data.T32VMJ.20250920T103741Z'
    }
    result = extract_mgrs_grid_code(umm_json)
    assert result == 'T32VMJ'


def test_extract_mgrs_grid_code_not_found_raises_key_error():
    """Test that KeyError is raised when MGRS grid code cannot be found."""
    umm_json = {
        'GranuleUR': 'test_granule_without_mgrs'
    }
    with pytest.raises(KeyError, match="MGRS_TILE_ID"):
        extract_mgrs_grid_code(umm_json)


def test_extract_mgrs_grid_code_missing_additional_attributes():
    """Test extraction when AdditionalAttributes doesn't have MGRS_TILE_ID."""
    umm_json = {
        'GranuleUR': 'short_id',
        'AdditionalAttributes': [
            {'Name': 'SOME_OTHER_ATTR', 'Values': ['value1']}
        ]
    }
    with pytest.raises(KeyError, match="MGRS_TILE_ID could not be extracted"):
        extract_mgrs_grid_code(umm_json)


# ---------------------------------------------------------------------------
# Tests for CustomDateTimeEncoder and json_dumps_with_datetime()
# ---------------------------------------------------------------------------

def test_custom_datetime_encoder():
    """Test CustomDateTimeEncoder converts datetime to ISO format."""
    dt = datetime(2025, 12, 31, 23, 59, 59)
    result = json.dumps({'date': dt}, cls=CustomDateTimeEncoder)
    assert '"2025-12-31T23:59:59"' in result


def test_json_dumps_with_datetime():
    """Test json_dumps_with_datetime handles datetime objects."""
    dt = datetime(2025, 1, 15, 10, 30, 45)
    obj = {
        'timestamp': dt,
        'name': 'test',
        'count': 42
    }
    result = json_dumps_with_datetime(obj)
    assert '"2025-01-15T10:30:45"' in result
    assert '"name": "test"' in result
    assert '"count": 42' in result


def test_json_dumps_with_datetime_nested():
    """Test json_dumps_with_datetime handles nested datetime objects."""
    dt1 = datetime(2025, 1, 1, 0, 0, 0)
    dt2 = datetime(2025, 12, 31, 23, 59, 59)
    obj = {
        'start': dt1,
        'end': dt2,
        'nested': {
            'timestamp': dt1
        }
    }
    result = json_dumps_with_datetime(obj)
    assert '"2025-01-01T00:00:00"' in result
    assert '"2025-12-31T23:59:59"' in result


# ---------------------------------------------------------------------------
# Tests for extract_granule_dates()
# ---------------------------------------------------------------------------

def test_extract_granule_dates_no_static_day():
    """Test extracting granule dates without static data day override."""
    umm_json = {
        'TemporalExtent': {
            'RangeDateTime': {
                'BeginningDateTime': '2025-03-15T12:00:00.000Z',
                'EndingDateTime': '2025-03-15T13:00:00.000Z'
            }
        }
    }
    begin, mid, end, dataday = extract_granule_dates(umm_json)

    assert begin == '2025-03-15T12:00:00.000000Z'
    assert mid == '2025-03-15T12:30:00.000000Z'
    assert end == '2025-03-15T13:00:00.000000Z'
    assert dataday == '2025074'  # March 15 is day 74


def test_extract_granule_dates_with_static_day():
    """Test extracting granule dates with static data day override."""
    umm_json = {
        'TemporalExtent': {
            'RangeDateTime': {
                'BeginningDateTime': '2025-06-15T10:00:00.000Z',
                'EndingDateTime': '2025-06-15T14:00:00.000Z'
            }
        }
    }
    static_day = 180
    begin, mid, end, dataday = extract_granule_dates(umm_json, static_day)

    assert begin == '2025-06-29T00:00:00.000000Z'  # Day 180 of 2025
    assert mid == '2025-06-29T00:00:00.000000Z'
    assert end == '2025-06-29T00:00:00.000000Z'
    assert dataday == '2025180'


def test_extract_granule_dates_leap_year():
    """Test extracting granule dates during a leap year."""
    umm_json = {
        'TemporalExtent': {
            'RangeDateTime': {
                'BeginningDateTime': '2024-02-29T00:00:00.000Z',
                'EndingDateTime': '2024-02-29T23:59:59.000Z'
            }
        }
    }
    begin, mid, end, dataday = extract_granule_dates(umm_json)

    assert '2024-02-29' in begin
    assert '2024-02-29' in mid
    assert '2024-02-29' in end
    assert dataday == '2024060'  # Feb 29 is day 60 in leap year


# ---------------------------------------------------------------------------
# Tests for parse_datetime()
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("datetime_str,expected_year,expected_month,expected_day", [
    ("2025-03-15T12:30:45.123456Z", 2025, 3, 15),
    ("2025-03-15T12:30:45Z", 2025, 3, 15),
    ("2025-03-15T12:30:45.123456+00:00", 2025, 3, 15),
    ("2025-03-15T12:30:45+00:00", 2025, 3, 15),
])
def test_parse_datetime_valid_formats(datetime_str, expected_year, expected_month, expected_day):
    """Test parsing various valid datetime formats."""
    result = parse_datetime(datetime_str)
    assert result.year == expected_year
    assert result.month == expected_month
    assert result.day == expected_day


def test_parse_datetime_invalid_format():
    """Test that invalid datetime format raises ValueError."""
    with pytest.raises(ValueError, match="Unable to parse datetime string"):
        parse_datetime("2025/03/15 12:30:45")


def test_parse_datetime_microseconds():
    """Test parsing datetime with microseconds."""
    result = parse_datetime("2025-03-15T12:30:45.123456Z")
    assert result.microsecond == 123456


# ---------------------------------------------------------------------------
# Tests for parse_doy()
# ---------------------------------------------------------------------------

def test_parse_doy_first_day():
    """Test parsing first day of year."""
    result = parse_doy(2025, 1)
    assert result == "2025-01-01T00:00:00.000000Z"


def test_parse_doy_last_day():
    """Test parsing last day of year."""
    result = parse_doy(2025, 365)
    assert result == "2025-12-31T00:00:00.000000Z"


def test_parse_doy_leap_year_last_day():
    """Test parsing last day of leap year."""
    result = parse_doy(2024, 366)
    assert result == "2024-12-31T00:00:00.000000Z"


def test_parse_doy_mid_year():
    """Test parsing mid-year day."""
    result = parse_doy(2025, 180)
    assert result == "2025-06-29T00:00:00.000000Z"


def test_parse_doy_leap_day():
    """Test parsing leap day."""
    result = parse_doy(2024, 60)
    assert result == "2024-02-29T00:00:00.000000Z"

@pytest.fixture(autouse=True)
def aws_region():
    os.environ["AWS_DEFAULT_REGION"] = "us-west-2"

# ---------------------------------------------------------------------------
# Tests for get_harmony_client()
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "input_env, expected_env",
    [
        ("UAT", Environment.UAT),
        ("PROD", Environment.PROD),
        ("SIT", Environment.UAT),  # defaults to UAT
    ]
)
@patch('bignbit.utils.boto3.client')
@patch('bignbit.utils.boto3.session.Session')
@patch('bignbit.utils.Client')
@patch('bignbit.utils.get_edl_creds')
def test_get_harmony_client_environments(
    mock_get_edl_creds,
    mock_harmony_client,
    mock_session,
    mock_boto,
    input_env,
    expected_env
):
    import bignbit.utils

    # --- creds ---
    mock_get_edl_creds.return_value = ('test_user', 'test_pass')

    # --- session / region ---
    mock_session.return_value.region_name = "us-west-2"

    # --- harmony client ---
    mock_client_instance = MagicMock()
    mock_harmony_client.return_value = mock_client_instance

    # --- lambda client ---
    mock_lambda = MagicMock()
    mock_boto.return_value = mock_lambda

    # 👇 double-encoded JSON (required by function)
    # inner = json.dumps({"access-token": "test-token"})
    # outer = json.dumps(inner).encode("utf-8")

    # mock_payload = MagicMock()
    # mock_payload.read.return_value = outer

    # mock_lambda.invoke.return_value = {
    #     "Payload": mock_payload
    # }

    # ---- payload must behave like AWS (realistic read()) ----
    payload_data = {
        "access-token": "test-token"
    }

    mock_payload = MagicMock()
    mock_payload.read.return_value = json.dumps(payload_data).encode("utf-8")

    mock_lambda.invoke.return_value = {
        "Payload": mock_payload
    }    

    # reset singleton
    bignbit.utils.HARMONY_CLIENT = None

    # --- execute ---
    result = bignbit.utils.get_harmony_client(input_env)

    # --- assertions ---
    assert result == mock_client_instance

    # verify correct environment passed to Client
    mock_harmony_client.assert_called_with(
        env=expected_env,
        token="test-token",
        should_validate_auth=bignbit.utils.HARMONY_SHOULD_VALIDATE_AUTH
    )