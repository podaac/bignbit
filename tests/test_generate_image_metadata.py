import json
import os
import xml.etree.ElementTree as ET

import bignbit.generate_image_metadata
from moto import mock_s3

import boto3
import botocore


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

@mock_s3
def test_process_static_data_day():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    cma_json = json.load(open(os.path.join(
        test_dir, 'sample_messages', 'generate_image_metadata',
        'cma.uat.input.OPERA_L3_DIST-ANN_mock.json')))

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
    s3_mock = boto3.client('s3')
    metadata_bucket = 'podaac-uat-cumulus-private'

    assert result
    # Assert two outputs, one image metadata xml and the other geotiff
    assert len(result['payload']['big']) == 2
    # Why is this any?
    assert any([r['subtype'] == 'ImageMetadata-v1.2' for r in result['payload']['big']])
    assert any([r['subtype'] == 'geotiff' for r in result['payload']['big']])
    for r in result['payload']['big']:
        metadata_xml = r['key']
        try:
            s3_mock.download_file(metadata_bucket, metadata_xml, r['fileName'])
        except botocore.exceptions.ClientError:
            print(f"could not stat s3://{metadata_bucket}/{metadata_xml}")
            continue
        md_tree = ET.parse(r['fileName'])
        md_root = md_tree.getroot()
        try:
            for child in md_root:
                if child.tag in ["DataStartDateTime", "DataMidDateTime", "DataEndDateTime"]:
                    assert child.text == "2023-01-01T00:00:00.000000Z"
                elif child.tag == "DataDay":
                    assert child.text == "2023001"
        finally:
            os.remove(r['fileName'])
        