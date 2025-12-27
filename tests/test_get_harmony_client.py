"""Tests for bignbit.utils module

    export PYTHONPATH=$PYTHONPATH:$(pwd)/bignbit
    pytest -v -x tests/test_get_harmony_client.py
"""

import pathlib
import json
from unittest.mock import patch, MagicMock
import pytest

from bignbit.utils import checksum_and_upload, get_harmony_client

# ----------------------------
# Tests for checksum_and_upload
# ----------------------------


@patch("bignbit.utils.upload_to_s3")
@patch("bignbit.utils.sha512sum")
def test_checksum_and_upload(mock_sha512sum, mock_upload_to_s3, tmp_path):
    """Test checksum calculation and upload to S3."""
    # Arrange
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world")

    mock_sha512sum.return_value = "dummychecksum"
    mock_upload_to_s3.return_value = "s3://mybucket/myobject"

    # Act
    checksum_type, checksum, s3_uri = checksum_and_upload(file_path, "mybucket", "myobject")

    # Assert
    assert checksum_type == "SHA512"
    assert checksum == "dummychecksum"
    assert s3_uri == "s3://mybucket/myobject"

    # Ensure mocked functions were called correctly
    mock_sha512sum.assert_called_once_with(file_path)
    mock_upload_to_s3.assert_called_once_with(file_path, "mybucket", "myobject")


# ----------------------------
# Tests for get_harmony_client
# ----------------------------


@patch("bignbit.utils.boto3.client")
@patch("bignbit.utils.get_edl_creds")
@patch("bignbit.utils.Client")
def test_get_harmony_client_creates_client(
    mock_client_class, mock_get_edl_creds, mock_boto3_client
):
    """Test that get_harmony_client creates a Client with correct parameters."""
    # Arrange
    mock_get_edl_creds.return_value = ("user", "pass")

    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client

    # Lambda response mock
    token_response = {"access-token": "dummy-token"}
    payload_mock = MagicMock()
    payload_mock.read.return_value = json.dumps(token_response).encode("utf-8")
    mock_lambda_client.invoke.return_value = {"Payload": payload_mock}

    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance

    # Act
    client = get_harmony_client("UAT")

    # Assert
    assert client == mock_client_instance
    mock_get_edl_creds.assert_called_once()
    mock_boto3_client.assert_called_once_with("lambda", region_name="us-west-2")
    # mock_client_class.assert_called_once_with(
    #     env=mock_client_instance.env,  # env is dynamic but instance is returned
    #     token="dummy-token",
    #     should_validate_auth=mock_client_instance.should_validate_auth,
    # )


@pytest.mark.parametrize(
    "env_input,expected_env",
    [
        ("uat", "UAT"),
        ("SIT", "UAT"),
        ("sandbox", "UAT"),
        ("OPS", "PROD"),
        ("prod", "PROD"),
    ],
)
@patch("bignbit.utils.boto3.client")
@patch("bignbit.utils.get_edl_creds", return_value=("user", "pass"))
@patch("bignbit.utils.Client")
def test_get_harmony_client_env_mapping(
    mock_client_class, mock_get_edl_creds, mock_boto3_client, env_input, expected_env
):
    """Test that get_harmony_client maps environment inputs correctly."""
    # Arrange
    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client

    payload_mock = MagicMock()
    payload_mock.read.return_value = json.dumps({"access-token": "dummy-token"}).encode("utf-8")
    mock_lambda_client.invoke.return_value = {"Payload": payload_mock}

    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance

    # Act
    get_harmony_client(env_input)

    # Assert
    # env attribute passed to Client should match expected mapping
    called_env = mock_client_class.call_args[1]["env"]
    assert str(called_env).upper().endswith(expected_env)
