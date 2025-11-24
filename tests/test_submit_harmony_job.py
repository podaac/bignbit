"""Unit tests for submit_harmony_job module"""
import datetime
from unittest.mock import Mock, patch

import pytest
from harmony import Collection, Request

from bignbit.submit_harmony_job import submit_harmony_job, generate_harmony_request


class TestSubmitHarmonyJob:
    """Test cases for submit_harmony_job function"""

    @patch('bignbit.submit_harmony_job.utils.get_harmony_client')
    @patch('bignbit.submit_harmony_job.generate_harmony_request')
    @patch('bignbit.submit_harmony_job.datetime')
    def test_submit_harmony_job_success(self, mock_datetime, mock_generate_request, mock_get_client):
        """Test successful harmony job submission"""
        mock_now = datetime.datetime(2023, 5, 15, 10, 30, 0, tzinfo=datetime.timezone.utc)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timezone.utc = datetime.timezone.utc
        
        mock_client = Mock()
        mock_job = Mock()
        mock_job.job_id = 'test-job-123'
        mock_client.submit.return_value = mock_job
        mock_client.request_as_url.return_value = 'https://harmony.earthdata.nasa.gov/test-url'
        mock_get_client.return_value = mock_client
        
        mock_request = Mock()
        mock_generate_request.return_value = mock_request
        
        cmr_env = 'UAT'
        collection_concept_id = 'C1234567890-POCLOUD'
        collection_name = 'TEST_COLLECTION'
        granule_concept_id = 'G1234567890-POCLOUD'
        granule_id = 'test_granule_001'
        variable = 'test_variable'
        output_width = '1024'
        output_height = '512'
        output_crs = 'EPSG:4326'
        big_config = {
            'config': {
                'width': 1024,
                'height': 512,
                'format': 'image/png',
                'outputCrs': ['EPSG:4326']
            }
        }
        bignbit_staging_bucket = 'podaac-sit-svc-internal'
        harmony_staging_path = 'harmony-output'
        
        result = submit_harmony_job(
            cmr_env, collection_concept_id, collection_name, granule_concept_id,
            granule_id, variable, output_width, output_height, output_crs, big_config,
            bignbit_staging_bucket, harmony_staging_path
        )
        
        expected_destination_url = 's3://podaac-sit-svc-internal/harmony-output/test_collection/20230515'
        mock_generate_request.assert_called_once_with(
            collection_concept_id, granule_concept_id, variable, output_width, output_height,
            output_crs, big_config, expected_destination_url
        )
        mock_get_client.assert_called_once_with(cmr_env)
        mock_client.submit.assert_called_once_with(mock_request)
        
        assert result == {
            'job': mock_job,
            'granule_id': granule_id,
            'granule_concept_id': granule_concept_id,
            'variable': variable,
            'output_crs': output_crs
        }

    @patch('bignbit.submit_harmony_job.utils.get_harmony_client')
    @patch('bignbit.submit_harmony_job.generate_harmony_request')
    @patch('bignbit.submit_harmony_job.datetime')
    def test_submit_harmony_job_with_different_collection_name_casing(self, mock_datetime, mock_generate_request, mock_get_client):
        """Test that collection name is properly lowercased in destination URL"""
        # Arrange
        mock_now = datetime.datetime(2023, 12, 25, 15, 45, 30, tzinfo=datetime.timezone.utc)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timezone.utc = datetime.timezone.utc
        
        mock_client = Mock()
        mock_job = Mock()
        mock_client.submit.return_value = mock_job
        mock_client.request_as_url.return_value = 'https://harmony.earthdata.nasa.gov/test-url'
        mock_get_client.return_value = mock_client
        
        mock_request = Mock()
        mock_generate_request.return_value = mock_request
        
        collection_name = 'MIXED_Case_Collection_NAME'
        
        submit_harmony_job(
            'OPS', 'C1234567890-POCLOUD', collection_name, 'G1234567890-POCLOUD',
            'test_granule', 'var1', '1024', '512', 'EPSG:4326', {'config': {'format': 'image/png'}},
            'bucket', 'path'
        )
        
        expected_destination_url = 's3://bucket/path/mixed_case_collection_name/20231225'
        mock_generate_request.assert_called_once()
        args, kwargs = mock_generate_request.call_args
        assert args[7] == expected_destination_url

    @patch('bignbit.submit_harmony_job.utils.get_harmony_client')
    def test_submit_harmony_job_client_error(self, mock_get_client):
        """Test handling of harmony client errors"""
        mock_client = Mock()
        mock_client.submit.side_effect = Exception("Harmony service unavailable")
        mock_get_client.return_value = mock_client

        with pytest.raises(Exception, match="Harmony service unavailable"):
            submit_harmony_job(
                'UAT', 'C1234567890-POCLOUD', 'test_collection', 'G1234567890-POCLOUD',
                'test_granule', 'variable', '1024', '512', 'EPSG:4326', {'config': {'format': 'image/png'}},
                'bucket', 'path'
            )


class TestGenerateHarmonyRequest:
    """Test cases for generate_harmony_request function"""

    def test_generate_harmony_request_with_defaults(self):
        """Test harmony request generation with default values"""
        collection_concept_id = 'C1234567890-POCLOUD'
        granule_concept_id = 'G1234567890-POCLOUD'
        variable = 'temperature'
        output_width = 512
        output_height = 256
        output_crs = 'EPSG:4326'
        big_config = {
            'config': {
                'width': 512,
                'height': 256
            }
        }
        destination_bucket_url = 's3://test-bucket/path/collection/20230515'
        
        result = generate_harmony_request(
            collection_concept_id, granule_concept_id, variable, output_width, output_height,
            output_crs, big_config, destination_bucket_url
        )
        
        assert isinstance(result, Request)
        assert result.collection.id == collection_concept_id
        assert result.granule_id == [granule_concept_id]
        assert result.variables == [variable]
        assert result.width == 512
        assert result.height == 256
        assert result.format == 'image/png'  # default value
        # assert result.crs == 'EPSG:4326'  # default value
        assert result.destination_url == destination_bucket_url

    def test_generate_harmony_request_with_custom_format_and_crs(self):
        """Test harmony request generation with custom format and CRS"""
        collection_concept_id = 'C9876543210-POCLOUD'
        granule_concept_id = 'G9876543210-POCLOUD'
        variable = 'chlorophyll_a'
        output_crs = 'EPSG:3857'
        output_width = 512
        output_height = 512
        big_config = {
            'config': {
                'format': 'image/jpeg',
                'outputCrs': 'EPSG:3857'
            }
        }
        destination_bucket_url = 's3://custom-bucket/custom-path/collection/20231201'
        
        result = generate_harmony_request(
            collection_concept_id, granule_concept_id, variable, output_width, output_height,
            output_crs, big_config, destination_bucket_url
        )
        
        assert isinstance(result, Request)
        assert result.collection.id == collection_concept_id
        assert result.granule_id == [granule_concept_id]
        assert result.variables == [variable]
        assert result.width == 512
        assert result.height == 512
        assert result.format == 'image/jpeg'
        assert result.crs == 'EPSG:3857'
        assert result.destination_url == destination_bucket_url

    def test_generate_harmony_request_with_all_parameters(self):
        """Test harmony request generation with all possible parameters"""
        collection_concept_id = 'C5555555555-DATACENTER'
        granule_concept_id = 'G5555555555-DATACENTER'
        variable = 'sea_surface_temperature'
        output_crs = 'EPSG:3413'
        output_width = 2048
        output_height = 1024
        big_config = {
            'config': {
                'width': 2048,
                'height': 1024,
                'format': 'image/tiff',
            }
        }
        destination_bucket_url = 's3://prod-bucket/harmony-results/sst_collection/20240101'
        
        result = generate_harmony_request(
            collection_concept_id, granule_concept_id, variable, output_width, output_height,
            output_crs, big_config, destination_bucket_url
        )

        assert isinstance(result, Request)
        assert result.collection.id == collection_concept_id
        assert result.granule_id == [granule_concept_id]
        assert result.variables == [variable]
        assert result.width == 2048
        assert result.height == 1024
        assert result.format == 'image/tiff'
        assert result.crs == 'EPSG:3413'
        assert result.destination_url == destination_bucket_url
        assert result.labels == ['bignbit']

    def test_generate_harmony_request_missing_config_keys(self):
        """Test harmony request generation with missing optional config keys uses defaults"""
        collection_concept_id = 'C1111111111-TEST'
        granule_concept_id = 'G1111111111-TEST'
        variable = 'wind_speed'
        output_crs = 'EPSG:4326'
        output_width = 1024
        output_height = 512
        big_config = {
            'config': {
                'width': 1024,
                'height': 512
            }
        }
        destination_bucket_url = 's3://test-bucket/results/wind/20230301'
        
        result = generate_harmony_request(
            collection_concept_id, granule_concept_id, variable, output_width, output_height,
            output_crs, big_config, destination_bucket_url
        )
        
        assert result.format == 'image/png'  # default
        # assert result.crs == 'EPSG:4326'  # default
        assert result.width == 1024
        assert result.height == 512

    def test_generate_harmony_request_collection_object(self):
        """Test that harmony request creates proper Collection object"""
        collection_concept_id = 'C7777777777-POCLOUD'
        granule_concept_id = 'G7777777777-POCLOUD'
        variable = 'precipitation'
        output_width = 1024
        output_height = 512
        output_crs = 'EPSG:4326'
        big_config = {'config': {'width': 256, 'height': 256}}
        destination_bucket_url = 's3://bucket/path'
        
        result = generate_harmony_request(
            collection_concept_id, granule_concept_id, variable, output_width, output_height,
            output_crs, big_config, destination_bucket_url
        )
        
        assert isinstance(result.collection, Collection)
        assert result.collection.id == collection_concept_id

    def test_generate_harmony_request_granule_id_list(self):
        """Test that granule_id is properly converted to list"""
        collection_concept_id = 'C8888888888-POCLOUD'
        granule_concept_id = 'G8888888888-POCLOUD'
        variable = 'humidity'
        output_width = 1024
        output_height = 512
        output_crs = 'EPSG:4326'
        big_config = {'config': {'width': 128, 'height': 128}}
        destination_bucket_url = 's3://bucket/path'
        
        result = generate_harmony_request(
            collection_concept_id, granule_concept_id, variable, output_width, output_height,
            output_crs, big_config, destination_bucket_url
        )
        
        assert isinstance(result.granule_id, list)
        assert len(result.granule_id) == 1
        assert result.granule_id[0] == granule_concept_id
        assert result.labels == ['bignbit']

    def test_generate_harmony_request_variables_list(self):
        """Test that variables parameter is properly converted to list"""
        collection_concept_id = 'C9999999999-POCLOUD'
        granule_concept_id = 'G9999999999-POCLOUD'
        variable = 'salinity'
        output_crs = 'EPSG:3857'
        output_width = 512
        output_height = 512
        big_config = {'config': {'width': 512, 'height': 512}}
        destination_bucket_url = 's3://bucket/path'
        
        result = generate_harmony_request(
            collection_concept_id, granule_concept_id, variable, output_width, output_height,
            output_crs, big_config, destination_bucket_url
        )
        
        assert isinstance(result.variables, list)
        assert len(result.variables) == 1
        assert result.variables[0] == variable
        assert result.labels == ['bignbit']


class TestSubmitHarmonyJobIntegration:
    """Integration-style tests for submit_harmony_job module"""

    @patch('bignbit.submit_harmony_job.utils.get_harmony_client')
    @patch('bignbit.submit_harmony_job.datetime')
    def test_full_workflow_integration(self, mock_datetime, mock_get_client):
        """Test the full workflow from parameters to harmony job submission"""
        mock_now = datetime.datetime(2023, 6, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timezone.utc = datetime.timezone.utc
        
        mock_client = Mock()
        mock_job = Mock()
        mock_job.job_id = 'integration-test-job-456'
        mock_client.submit.return_value = mock_job
        mock_client.request_as_url.return_value = 'https://harmony.earthdata.nasa.gov/integration-test'
        mock_get_client.return_value = mock_client
        
        cmr_env = 'OPS'
        collection_concept_id = 'C1596878748-POCLOUD'
        collection_name = 'MUR-JPL-L4-GLOB-v4.1'
        granule_concept_id = 'G1596878748-POCLOUD'
        granule_id = 'test_granule_integration'
        variable = 'analysed_sst'
        output_width = 1024
        output_height = 512
        output_crs = 'EPSG:3413'
        big_config = {
            'config': {
                'width': 1024,
                'height': 512,
                'format': 'image/png',
                'outputCrs': ['EPSG:4326', 'EPSG:3413']
            }
        }
        bignbit_staging_bucket = 'podaac-sit-svc-internal'
        harmony_staging_path = 'bignbit-cnm-output'
        
        result = submit_harmony_job(
            cmr_env, collection_concept_id, collection_name, granule_concept_id,
            granule_id, variable, output_width, output_height, output_crs, big_config,
            bignbit_staging_bucket, harmony_staging_path
        )
        
        # Verify the harmony client was called correctly
        mock_get_client.assert_called_once_with(cmr_env)
        mock_client.submit.assert_called_once()
        
        # Verify the request object passed to submit
        submitted_request = mock_client.submit.call_args[0][0]
        assert isinstance(submitted_request, Request)
        assert submitted_request.collection.id == collection_concept_id
        assert submitted_request.granule_id == [granule_concept_id]
        assert submitted_request.variables == [variable]
        assert submitted_request.width == 1024
        assert submitted_request.height == 512
        assert submitted_request.format == 'image/png'
        assert submitted_request.crs == 'EPSG:3413'
        
        expected_destination_url = 's3://podaac-sit-svc-internal/bignbit-cnm-output/mur-jpl-l4-glob-v4.1/20230601'
        assert submitted_request.destination_url == expected_destination_url
        
        # Verify the returned harmony job structure
        assert result['job'] == mock_job
        assert result['granule_id'] == granule_id
        assert result['granule_concept_id'] == granule_concept_id
        assert result['variable'] == variable