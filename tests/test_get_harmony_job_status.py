"""Unit tests for get_harmony_job_status module"""
from unittest.mock import MagicMock, patch

import pytest
import requests
from moto import mock_s3

import bignbit.utils
from bignbit.get_harmony_job_status import (
    check_harmony_job,
    HarmonyJobNoDataError,
    HarmonyTransientError,
)


@pytest.mark.vcr
@mock_s3
def test_process_results_no_data():
    """Test that HarmonyJobNoDataError is raised when Harmony returns no data"""
    bignbit.utils.ED_USER = 'test'
    bignbit.utils.ED_PASS = 'test'

    # Note: This test uses VCR to record the Harmony API response
    # The cassette should show a successful job with no result URLs
    # Using UAT environment since the test job ID exists in UAT
    with pytest.raises(HarmonyJobNoDataError) as exc_info:
        check_harmony_job('60c6de41-a51a-4283-aa7c-2d530ebab8d9', 'uat', 'test_variable', 'EPSG:4326')

    assert 'no data' in str(exc_info.value).lower()
    assert 'test_variable' in str(exc_info.value)
    assert 'EPSG:4326' in str(exc_info.value)


def _make_http_error(status_code):
    """Build a requests.exceptions.HTTPError with a mocked response."""
    response = MagicMock()
    response.status_code = status_code
    error = requests.exceptions.HTTPError(response=response)
    return error


@patch('bignbit.get_harmony_job_status.utils.get_harmony_client')
def test_check_harmony_job_raises_transient_error_on_500(mock_get_client):
    """Test that HarmonyTransientError is raised when Harmony status returns a 500."""
    bignbit.utils.ED_USER = 'test'
    bignbit.utils.ED_PASS = 'test'

    mock_client = MagicMock()
    mock_client.status.side_effect = _make_http_error(500)
    mock_get_client.return_value = mock_client

    with pytest.raises(HarmonyTransientError) as exc_info:
        check_harmony_job('test-job-id', 'uat', 'test_variable', 'EPSG:4326')

    assert 'transient error' in str(exc_info.value).lower()
    assert 'test-job-id' in str(exc_info.value)


@patch('bignbit.get_harmony_job_status.utils.get_harmony_client')
def test_check_harmony_job_raises_transient_error_on_503(mock_get_client):
    """Test that HarmonyTransientError is raised when Harmony status returns a 503."""
    bignbit.utils.ED_USER = 'test'
    bignbit.utils.ED_PASS = 'test'

    mock_client = MagicMock()
    mock_client.status.side_effect = _make_http_error(503)
    mock_get_client.return_value = mock_client

    with pytest.raises(HarmonyTransientError):
        check_harmony_job('test-job-id', 'uat', 'test_variable', 'EPSG:4326')


@patch('bignbit.get_harmony_job_status.utils.get_harmony_client')
def test_check_harmony_job_reraises_non_5xx_http_error(mock_get_client):
    """Test that non-5xx HTTPErrors (e.g. 404) are re-raised without wrapping."""
    bignbit.utils.ED_USER = 'test'
    bignbit.utils.ED_PASS = 'test'

    mock_client = MagicMock()
    mock_client.status.side_effect = _make_http_error(404)
    mock_get_client.return_value = mock_client

    with pytest.raises(requests.exceptions.HTTPError):
        check_harmony_job('test-job-id', 'uat', 'test_variable', 'EPSG:4326')


@patch('bignbit.get_harmony_job_status.utils.get_harmony_client')
def test_check_harmony_job_result_urls_raises_transient_error_on_500(mock_get_client):
    """Test that HarmonyTransientError is raised when result_urls call returns a 500."""
    bignbit.utils.ED_USER = 'test'
    bignbit.utils.ED_PASS = 'test'

    mock_client = MagicMock()
    mock_client.status.return_value = {'status': 'successful'}
    mock_client.result_urls.side_effect = _make_http_error(500)
    mock_get_client.return_value = mock_client

    with pytest.raises(HarmonyTransientError) as exc_info:
        check_harmony_job('test-job-id', 'uat', 'test_variable', 'EPSG:4326')

    assert 'result urls' in str(exc_info.value).lower()
    assert 'test-job-id' in str(exc_info.value)