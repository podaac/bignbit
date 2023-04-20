import json
import os

import bignbit.generate_image_metadata
from moto import mock_s3

import boto3


@mock_s3
def test_process_opera_input():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    cma_json = json.load(open(os.path.join(
        test_dir, 'sample_messages', 'generate_image_metadata',
        'cma.uat.input.OPERA_L3_DSWx-HLS_T48SUE_20190302T034350Z_20230131T222341Z_L8_30_v0.0.json')))

    buckets_to_create = set([b['name'] for _, b in cma_json['cma']['event']['meta']['buckets'].items()])
    buckets_to_create = buckets_to_create.union(
        set([granule_file['bucket'] for granule in cma_json['cma']['event']['payload']['granules'] for granule_file in
             granule['files']]))

    for bucket_name in buckets_to_create:
        if "*" in bucket_name:
            continue
        aws_s3 = boto3.resource('s3', region_name='us-east-1')
        aws_s3.create_bucket(Bucket=bucket_name)

    result = bignbit.generate_image_metadata.lambda_handler(cma_json, {})

    assert result
    # Assert two outputs, one image metadata xml and the other geotiff
    assert len(result['payload']['big']) == 2
    assert any([r['subtype'] == 'ImageMetadata-v1.2' for r in result['payload']['big']])
    assert any([r['subtype'] == 'geotiff' for r in result['payload']['big']])
