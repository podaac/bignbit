"""Unit tests for process_harmony_results module"""
import datetime
import json
from unittest.mock import Mock, patch

import boto3
import pytest
from harmony import Collection, Request
from moto import mock_s3

from bignbit.process_harmony_results import process_results

@pytest.mark.vcr
@mock_s3
def test_process_results():
    import bignbit.utils
    bignbit.utils.ED_USER = 'test'
    bignbit.utils.ED_PASS = 'test'

    aws_s3 = boto3.resource('s3', region_name='us-east-1')
    bucket = aws_s3.create_bucket(Bucket='svc-bignbit-podaac-ops-cumulus-staging')
    keys = ['bignbit-harmony-output/opera_l3_dswx-s1_v1/20250918/d449048b-b00a-40dc-85d8-615eb4006a63/110446591/OPERA_L3_DSWx-S1_T35VNH_20250907T154901Z_20250908T000337Z_S1A_30_v1.0_B01_WTR.png',
     'bignbit-harmony-output/opera_l3_dswx-s1_v1/20250918/d449048b-b00a-40dc-85d8-615eb4006a63/110446591/OPERA_L3_DSWx-S1_T35VNH_20250907T154901Z_20250908T000337Z_S1A_30_v1.0_B01_WTR.pgw',
     'bignbit-harmony-output/opera_l3_dswx-s1_v1/20250918/d449048b-b00a-40dc-85d8-615eb4006a63/110446591/OPERA_L3_DSWx-S1_T35VNH_20250907T154901Z_20250908T000337Z_S1A_30_v1.0_B01_WTR.png.aux.xml']
    for key in keys:
        bucket.put_object(Body=b'bytes', Key=key)

    results = process_results('d449048b-b00a-40dc-85d8-615eb4006a63', 'ops', 'all', 'epsg:test')

    assert results
    assert len(results) == 3
    assert 'output_crs' in next(iter(results))
    assert 'EPSG:TEST' == next(iter(results))['output_crs']
