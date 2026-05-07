"""Unit tests for get_harmony_job_status module"""

import json
from unittest.mock import MagicMock, patch

import pytest

import bignbit.utils
from bignbit.get_harmony_job_status import (
    check_harmony_job,
    HarmonyJobNoDataError
)


@pytest.mark.vcr
@patch('bignbit.utils.get_harmony_client')
@patch('bignbit.utils.get_edl_creds')
@patch('bignbit.utils.boto3.client')
def test_process_results_no_data(
    mock_boto,
    mock_get_edl_creds,
    mock_get_harmony_client
):
    """Test HarmonyJobNoDataError is raised when no results are returned"""

    # ---- creds ----
    mock_get_edl_creds.return_value = ('test_user', 'test_pass')

    # ---- lambda client ----
    mock_lambda = MagicMock()
    mock_boto.return_value = mock_lambda

    payload_data = {
        "access-token": "test-token"
    }

    mock_payload = MagicMock()
    mock_payload.read.return_value = json.dumps(payload_data).encode("utf-8")

    mock_lambda.invoke.return_value = {
        "Payload": mock_payload
    }

    # ---- harmony client ----
    mock_harmony_client = MagicMock()

    # simulate empty Harmony results
    mock_harmony_client.result_urls.return_value = []

    # serializable status response
    mock_harmony_client.status.return_value = {
        "status": "successful",
        "message": "No data found"
    }

    mock_get_harmony_client.return_value = mock_harmony_client

    # optional globals
    bignbit.utils.ED_USER = "test"
    bignbit.utils.ED_PASS = "test"

    # ---- assertion ----
    with pytest.raises(HarmonyJobNoDataError) as exc_info:
        check_harmony_job(
            '60c6de41-a51a-4283-aa7c-2d530ebab8d9',
            'uat',
            'test_variable',
            'EPSG:4326'
        )

    msg = str(exc_info.value).lower()

    assert "no data" in msg
    assert "test_variable" in msg
    assert "epsg:4326" in msg

    # ---- verify mocks ----
    mock_get_harmony_client.assert_called_once_with('uat')

    mock_harmony_client.result_urls.assert_called_once()

    mock_harmony_client.status.assert_called()