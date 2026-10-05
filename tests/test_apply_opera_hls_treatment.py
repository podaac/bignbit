import json
import pathlib
import urllib.request
from os.path import dirname, realpath
from unittest.mock import patch, MagicMock

import pytest

from bignbit.apply_opera_hls_treatment import the_opera_hls_treatment, get_file


@pytest.fixture()
def cnm_v151_schema():
    cnm_v151_url = "https://raw.githubusercontent.com/podaac/cloud-notification-message-schema/v1.5.1/cumulus_sns_schema.json"
    cnm_schema = json.loads(urllib.request.urlopen(cnm_v151_url).read().decode("utf-8"))
    return cnm_schema


def test_the_opera_hls_treatment(tmp_path):
    test_data_input = pathlib.Path(dirname(realpath(__file__))).joinpath('data').joinpath(
        'OPERA_L3_DSWx-HLS_T48SUE_20190302T034350Z_20230131T222341Z_L8_30_v0.0_BROWSE.tiff')

    result = the_opera_hls_treatment(test_data_input, tmp_path, 'T48SUE')

    assert result


@patch('bignbit.apply_opera_hls_treatment.boto3')
def test_get_file_requester_pays(mock_boto3, tmp_path):
    """Requester pays should set RequestPayer on the download call."""
    mock_obj = MagicMock()
    mock_boto3.resource.return_value.Bucket.return_value.Object.return_value = mock_obj

    local_filepath = tmp_path.joinpath('download.tiff')
    get_file('some-bucket', 'some/key.tiff', local_filepath, requester_pays=True)

    _, kwargs = mock_obj.download_fileobj.call_args
    assert kwargs['ExtraArgs'] == {'RequestPayer': 'requester'}


@patch('bignbit.apply_opera_hls_treatment.boto3')
def test_get_file_no_requester_pays(mock_boto3, tmp_path):
    """Without requester pays, no RequestPayer args should be sent."""
    mock_obj = MagicMock()
    mock_boto3.resource.return_value.Bucket.return_value.Object.return_value = mock_obj

    local_filepath = tmp_path.joinpath('download.tiff')
    get_file('some-bucket', 'some/key.tiff', local_filepath)

    _, kwargs = mock_obj.download_fileobj.call_args
    assert kwargs['ExtraArgs'] is None
