"""Unit tests for get_harmony_job_status module"""
import pytest
from moto import mock_s3
from unittest.mock import patch, MagicMock

import bignbit.utils
from bignbit.get_harmony_job_status import check_harmony_job, HarmonyJobNoDataError


@pytest.mark.vcr
@mock_s3
@patch('bignbit.utils.get_edl_creds')
@patch('bignbit.utils.boto3.client')
def test_process_results_no_data(mock_boto, mock_get_creds):
    """Test that HarmonyJobNoDataError is raised when Harmony returns no data"""
    mock_lambda = MagicMock()
    mock_boto.return_value = mock_lambda

    mock_lambda.invoke.return_value = {
        "Payload": MagicMock(
            read=lambda: b'"{\\"status\\": \\"SUCCESS\\", \\"results\\": []}"'
        )
    }
    
    mock_get_creds.return_value = {
        "access-token": "test-token"
    }

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