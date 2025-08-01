import json
import os
import xml.etree.ElementTree as ET

import pytest

import bignbit.generate_image_metadata
from moto import mock_s3

import boto3
import botocore


def create_mock_buckets(cma_json):
    """
    Create mock S3 buckets for testing purposes.
    """
    buckets_to_create = set([b['name'] for _, b in cma_json['cma']['event']['meta']['buckets'].items()])
    buckets_to_create = buckets_to_create.union(
        set([granule_file['bucket'] for granule in cma_json['cma']['event']['payload']['granules'] for granule_file in
             granule['files']]))

    for bucket_name in buckets_to_create:
        if "*" in bucket_name:
            continue
        aws_s3 = boto3.resource('s3', region_name='us-east-1')
        aws_s3.create_bucket(Bucket=bucket_name)

@mock_s3
def test_process_opera_input():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    cma_json = json.load(open(os.path.join(
        test_dir, 'sample_messages', 'generate_image_metadata',
        'cma.uat.input.OPERA_L3_DSWx-HLS_T48SUE_20190302T034350Z_20230131T222341Z_L8_30_v0.0.json')))

    create_mock_buckets(cma_json)

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

    create_mock_buckets(cma_json)

    result = bignbit.generate_image_metadata.lambda_handler(cma_json, {})
    s3_mock = boto3.client('s3')
    metadata_bucket = 'podaac-uat-cumulus-private'

    assert result
    # Assert two outputs, one image metadata xml and the other geotiff
    assert len(result['payload']['big']) == 2
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


@mock_s3
@pytest.mark.parametrize("subdaily", [True, False])
def test_process_subdaily(subdaily: bool):
    test_dir = os.path.dirname(os.path.realpath(__file__))
    cma_json = json.load(open(os.path.join(
        test_dir, 'sample_messages', 'generate_image_metadata',
        'cma.uat.input.TEMPO_NO2_L3.json')))

    cma_json['cma']['event']['payload']['datasetConfigurationForBIG']['config']['subdaily'] = subdaily
    expected_xml_tags = [('DataStartDateTime', '2025-04-22T11:47:02.000000Z'),
                         ('DataMidDateTime', '2025-04-22T12:06:56.500000Z'),
                         ('DataEndDateTime', '2025-04-22T12:26:51.000000Z'),
                         ('DataDateTime', '2025-04-22T11:47:02.000000Z')]
    if not subdaily:
        # If subdaily is False, we expect the DataDateTime to not be present in the metadata XML
        expected_xml_tags = list(filter(lambda t: t[0] != 'DataDateTime', expected_xml_tags))

    create_mock_buckets(cma_json)
    result = bignbit.generate_image_metadata.lambda_handler(cma_json, {})

    assert result
    # Assert two outputs, the image and the image metadata xml
    assert len(result['payload']['big']) == 2
    assert 'metadata' in [r['type'] for r in result['payload']['big']]

    # Download the metadata XML file and check the contents are as expected
    result_metadata_xml = next(filter(lambda r: r['type'] == 'metadata', result['payload']['big']))
    result_metadata_xml_filename = result_metadata_xml['fileName']
    s3_mock = boto3.client('s3')
    s3_mock.download_file(result_metadata_xml['bucket'], result_metadata_xml['key'], result_metadata_xml_filename)
    actual_xml_tags = []
    md_tree = ET.parse(result_metadata_xml_filename)
    md_root = md_tree.getroot()
    try:
        for child in md_root:
            for tag, text in expected_xml_tags:
                if child.tag == tag:
                    assert child.text == text
                    actual_xml_tags.append((child.tag, child.text))
    finally:
        os.remove(result_metadata_xml_filename)

    assert expected_xml_tags == actual_xml_tags
