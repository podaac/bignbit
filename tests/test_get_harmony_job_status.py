"""Unit tests for get_harmony_job_status module"""
import pytest
from moto import mock_s3

import bignbit.utils
from bignbit.get_harmony_job_status import check_harmony_job, HarmonyJobNoDataError


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