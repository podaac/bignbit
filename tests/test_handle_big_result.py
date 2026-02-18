"""Unit tests for handle_big_result module"""
import hashlib
import json
import xml.etree.ElementTree as ET
import boto3
import pytest
from moto import mock_s3

import bignbit.utils
from bignbit.handle_big_result import (
    construct_cnm,
    create_metadata_xml,
    generate_metadata,
    get_mdxml_cnm_file_meta,
    process_harmony_results,
    write_cnm_message
)
from bignbit.image_set import ImageSet

@pytest.mark.vcr
@mock_s3
def test_process_harmony_results():
    """Test pulling results of a harmony job from s3."""
    bignbit.utils.ED_USER = 'test'
    bignbit.utils.ED_PASS = 'test'
    job_id = '3d276f84-56e2-4f0a-acb2-35b9fcaaa317'

    # Create mock S3 bucket and populate with test data
    s3_client = boto3.client('s3', region_name='us-west-2')
    bucket_name = 'harmony-uat-staging'
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )

    # Dummy files for harmony request
    image_key = f'public/{job_id}/9202859/PREFIRE_SAT2_2B-FLX_S07_R00_20210721013413_03040.nc.G00.png'
    image_data = b'fake image data for testing'
    wld_key = f'public/{job_id}/9202859/PREFIRE_SAT2_2B-FLX_S07_R00_20210721013413_03040.nc.G00.pgw'
    wld_data = b'fake world file for testing'
    aux_key = f'public/{job_id}/9202859/PREFIRE_SAT2_2B-FLX_S07_R00_20210721013413_03040.nc.G00.png.aux.xml'
    aux_data = b'fake png aux xml metadata for testing'
    for key, data in [(image_key, image_data), (wld_key, wld_data), (aux_key, aux_data)]:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=data
        )

    harmony_job = {
        'job': job_id,
        'granule_id': 'PREFIRE_SAT2_2B-FLX_S07_R00_20210721013413_03040.nc.G00.tif',
        'granule_concept_id': 'G1263096192-EEDTEST',
        'variable': 'flx',
        'output_crs': 'EPSG:3413',
        'status': 'successful'
    }
    cmr_environment = 'UAT'
    file_dicts = process_harmony_results(harmony_job, cmr_environment)
    assert len(file_dicts) == 3
    for file in file_dicts:
        assert file['output_crs'] == 'EPSG:3413'
        assert file['variable'] == 'flx'

@pytest.mark.vcr
def test_process_harmony_results_no_data():
    """Test case where a harmony job returned no data and was passed empty."""
    bignbit.utils.ED_USER = 'test'
    bignbit.utils.ED_PASS = 'test'

    harmony_job = {}
    cmr_environment = 'UAT'
    file_dicts = process_harmony_results(harmony_job, cmr_environment)
    assert file_dicts == []

@mock_s3
def test_generate_metadata():
    """Test generating image metadata xml end-to-end for a single image set."""
    # image metadata xml will be uploaded within the function, so the bucket needs to be mocked
    s3_client = boto3.client('s3', region_name='us-west-2')
    bucket_name = 'svc-bignbit-podaac-sit-svc-staging'
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )

    image_set = ImageSet(
        name='test_2021202_EPSG:3413!C1263096190-EEDTEST',
        image={
            'fileName': 'PREFIRE_SAT2_2B-FLX_S07_R00_20210721013413_03040.nc.G00.png',
            'bucket': 'svc-bignbit-podaac-sit-svc-staging',
            'key': 'bignbit-harmony-output/prefire_sat2_2b-flx_eedtest/test/test/PREFIRE_SAT2_2B-FLX_S07_R00_20210721013413_03040.nc.G00.png',
            'type': 'browse',
            'subtype': 'png',
            'variable': 'flx',
            'output_crs': 'EPSG:3413',
            'dataday': '2021202'
        },
        world_file={
            'fileName': 'PREFIRE_SAT2_2B-FLX_S07_R00_20210721013413_03040.nc.G00.pgw',
            'bucket': 'svc-bignbit-podaac-sit-svc-staging',
            'key': 'bignbit-harmony-output/prefire_sat2_2b-flx_eedtest/test/test/PREFIRE_SAT2_2B-FLX_S07_R00_20210721013413_03040.nc.G00.pgw',
            'type': 'metadata',
            'subtype': 'world file',
            'variable': 'flx',
            'output_crs': 'EPSG:3413',
            'dataday': '2021202'
        }
    )
    begin = '2021-07-21T01:34:13.165Z'
    mid = '2021-07-21T02:21:51.985Z'
    end = '2021-07-21T03:09:30.805Z'
    data_day = '2021202'
    subdaily = True
    partial_id = None
    updated_image_set = generate_metadata(
        image_set,
        begin, mid, end, data_day,
        subdaily,
        partial_id
    )
    assert updated_image_set is not None
    assert updated_image_set.image_metadata['fileName'] == 'PREFIRE_SAT2_2B-FLX_S07_R00_20210721013413_03040.nc.G00.xml'
    assert updated_image_set.image_metadata['type'] == 'metadata'
    assert updated_image_set.image_metadata['subtype'] == 'ImageMetadata-v1.2'


def test_create_metadata_xml_subdaily():
    """Test creating metadata XML for subdaily products"""
    begin = '2021-07-21T01:34:13.165Z'
    mid = '2021-07-21T02:21:51.985Z'
    end = '2021-07-21T03:09:30.805Z'
    data_day = '2021202'
    subdaily = True
    partial_id = None

    xml_bytes = create_metadata_xml(begin, mid, end, data_day, subdaily, partial_id)

    # Parse the XML to verify structure
    root = ET.fromstring(xml_bytes)
    assert root.tag == 'ImageryMetadata'

    # Check required elements
    assert root.find('ProviderProductionDateTime') is not None
    data_start = root.find('DataStartDateTime')
    assert data_start is not None and data_start.text == begin
    data_mid = root.find('DataMidDateTime')
    assert data_mid is not None and data_mid.text == mid
    data_end = root.find('DataEndDateTime')
    assert data_end is not None and data_end.text == end

    # For subdaily, should have DataDateTime instead of DataDay
    data_datetime = root.find('DataDateTime')
    assert data_datetime is not None
    assert data_datetime.text == begin
    assert root.find('DataDay') is None

    # No partial ID for this test
    assert root.find('PartialId') is None


def test_create_metadata_xml_daily():
    """Test creating metadata XML for daily products"""
    begin = '2021-07-21T00:00:00.000Z'
    mid = '2021-07-21T12:00:00.000Z'
    end = '2021-07-21T23:59:59.999Z'
    data_day = '2021202'
    subdaily = False
    partial_id = None

    xml_bytes = create_metadata_xml(begin, mid, end, data_day, subdaily, partial_id)

    root = ET.fromstring(xml_bytes)

    # For daily products, should have DataDay instead of DataDateTime
    data_day_elem = root.find('DataDay')
    assert data_day_elem is not None
    assert data_day_elem.text == data_day
    assert root.find('DataDateTime') is None


def test_create_metadata_xml_with_partial_id():
    """Test creating metadata XML with partial ID (OPERA HLS)"""
    begin = '2021-07-21T00:00:00.000Z'
    mid = '2021-07-21T12:00:00.000Z'
    end = '2021-07-21T23:59:59.999Z'
    data_day = '2021202'
    subdaily = False
    partial_id = '11SKA'

    xml_bytes = create_metadata_xml(begin, mid, end, data_day, subdaily, partial_id)

    root = ET.fromstring(xml_bytes)

    # Should have PartialId element
    partial_id_elem = root.find('PartialId')
    assert partial_id_elem is not None
    assert partial_id_elem.text == partial_id


def test_get_mdxml_cnm_file_meta():
    """Test creating CNM file metadata for image metadata XML"""
    image_metadata_xml = b'<ImageryMetadata>test</ImageryMetadata>'

    cnm_file_meta = {
        'fileName': 'test_image.png',
        'bucket': 'test-bucket',
        'key': 'path/to/test_image.png',
        'checksum': 'abc123',
        'checksumType': 'md5',
        'variable': 'temperature',
        'output_crs': 'EPSG:4326'
    }

    result = get_mdxml_cnm_file_meta(image_metadata_xml, cnm_file_meta)

    # Check that basic properties are copied
    assert result['bucket'] == 'test-bucket'
    assert result['variable'] == 'temperature'
    assert result['output_crs'] == 'EPSG:4326'

    # Check that file-specific properties are updated
    assert result['fileName'] == 'test_image.xml'
    assert result['key'] == 'path/to/test_image.xml'
    assert result['type'] == 'metadata'
    assert result['subtype'] == 'ImageMetadata-v1.2'

    # Check that checksum is SHA512
    assert result['checksumType'] == 'SHA512'
    expected_checksum = hashlib.sha512(image_metadata_xml).hexdigest()
    assert result['checksum'] == expected_checksum

    # Check that size is set
    assert result['size'] == len(image_metadata_xml)


@mock_s3
def test_write_cnm_message():
    """Test writing CNM message to S3"""
    # Create mock S3 bucket
    s3_client = boto3.client('s3', region_name='us-west-2')
    bucket_name = 'test-audit-bucket'
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )

    # Create test image set
    image_set = ImageSet(
        name='test_image_2021202_EPSG:4326!G1234567890-TESTPROV',
        image={
            'fileName': 'test_image.png',
            'bucket': 'test-bucket',
            'key': 'path/to/test_image.png',
            'variable': 'temperature',
            'output_crs': 'EPSG:4326'
        },
        world_file={
            'fileName': 'test_image.pgw',
            'bucket': 'test-bucket',
            'key': 'path/to/test_image.pgw'
        },
        image_metadata={
            'fileName': 'test_image.xml',
            'bucket': 'test-bucket',
            'key': 'path/to/test_image.xml',
            'type': 'metadata',
            'subtype': 'ImageMetadata-v1.2'
        }
    )

    cmr_provider = 'TESTPROV'
    collection_name = 'TEST_COLLECTION'
    granule_id = 'test_granule_id'
    bignbit_audit_path = 'bignbit-cnm-output'

    # Write CNM message
    cnm_key = write_cnm_message(
        image_set,
        cmr_provider,
        collection_name,
        granule_id,
        bucket_name,
        bignbit_audit_path
    )

    # Verify the key format
    assert cnm_key.startswith(f'{bignbit_audit_path}/')
    assert collection_name in cnm_key
    assert granule_id in cnm_key
    assert cnm_key.endswith('.cnm.json')

    # Verify the file was uploaded to S3
    response = s3_client.get_object(Bucket=bucket_name, Key=cnm_key)
    cnm_content = response['Body'].read()

    # Verify it's valid JSON
    cnm_message = json.loads(cnm_content)
    assert cnm_message['provider'] == cmr_provider
    assert cnm_message['identifier'] == image_set.name


def test_construct_cnm_with_crs():
    """Test constructing CNM message with output CRS suffix"""
    image_set = ImageSet(
        name='test_image_2021202_EPSG:3413!G1234567890-TESTPROV',
        image={
            'fileName': 'test_image.png',
            'bucket': 'test-bucket',
            'key': 'path/to/test_image.png',
            'variable': 'temperature',
            'output_crs': 'EPSG:3413'
        },
        world_file={
            'fileName': 'test_image.pgw',
            'bucket': 'test-bucket',
            'key': 'path/to/test_image.pgw'
        },
        image_metadata={
            'fileName': 'test_image.xml',
            'bucket': 'test-bucket',
            'key': 'path/to/test_image.xml',
            'type': 'metadata',
            'subtype': 'ImageMetadata-v1.2'
        }
    )

    cmr_provider = 'TESTPROV'
    collection_name = 'TEST_COLLECTION'

    cnm = construct_cnm(image_set, cmr_provider, collection_name)

    # Verify CNM structure
    assert cnm['version'] == '1.5.1'
    assert cnm['duplicationid'] == image_set.name
    assert cnm['identifier'] == image_set.name
    assert cnm['provider'] == cmr_provider
    assert cnm['submissionTime'] is not None

    # Verify collection name includes CRS suffix (N for EPSG:3413)
    assert cnm['collection'] == 'TEST_COLLECTION_temperature_N'

    # Verify product structure
    assert 'product' in cnm
    assert 'files' in cnm['product']
    assert len(cnm['product']['files']) == 3  # image, world file, metadata


def test_construct_cnm_without_crs():
    """Test constructing CNM message without output CRS and no world file"""
    image_set = ImageSet(
        name='test_image_2021202!G1234567890-TESTPROV',
        image={
            'fileName': 'test_image.tif',
            'bucket': 'test-bucket',
            'key': 'path/to/test_image.tif',
            'variable': 'water_index'
        },
        image_metadata={
            'fileName': 'test_image.xml',
            'bucket': 'test-bucket',
            'key': 'path/to/test_image.xml',
            'type': 'metadata',
            'subtype': 'ImageMetadata-v1.2'
        }
    )

    cmr_provider = 'TESTPROV'
    collection_name = 'OPERA_L3_DSWX-HLS'

    cnm = construct_cnm(image_set, cmr_provider, collection_name)

    # Verify collection name doesn't have CRS suffix when output_crs is not present
    assert cnm['collection'] == 'OPERA_L3_DSWX-HLS_water_index'


def test_construct_cnm_crs_suffixes():
    """Test that different CRS values produce correct suffixes"""
    test_cases = [
        ('EPSG:4326', 'LL'),  # Geographic
        ('EPSG:3413', 'N'),   # North Polar
        ('EPSG:3031', 'S'),   # South Polar
    ]

    for crs, expected_suffix in test_cases:
        image_set = ImageSet(
            name=f'test_{crs}',
            image={
                'fileName': 'test.png',
                'bucket': 'bucket',
                'key': 'key',
                'variable': 'var',
                'output_crs': crs
            },
            world_file={
                'fileName': 'test.pgw',
                'bucket': 'bucket',
                'key': 'key'
            },
            image_metadata={
                'fileName': 'test.xml',
                'bucket': 'bucket',
                'key': 'key',
                'type': 'metadata',
                'subtype': 'ImageMetadata-v1.2'
            }
        )

        cnm = construct_cnm(image_set, 'PROV', 'COLLECTION')
        assert cnm['collection'] == f'COLLECTION_var_{expected_suffix}'


