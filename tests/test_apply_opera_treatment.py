import json
import pathlib
import urllib.request
from os.path import dirname, realpath

import pytest

from bignbit.apply_opera_treatment import the_opera_treatment


@pytest.fixture()
def cnm_v151_schema():
    cnm_v151_url = "https://raw.githubusercontent.com/podaac/cloud-notification-message-schema/v1.5.1/cumulus_sns_schema.json"
    cnm_schema = json.loads(urllib.request.urlopen(cnm_v151_url).read().decode("utf-8"))
    return cnm_schema


def test_the_opera_treatment(tmp_path):
    test_data_input = pathlib.Path(dirname(realpath(__file__))).joinpath('data').joinpath(
        'OPERA_L3_DSWx-HLS_T48SUE_20190302T034350Z_20230131T222341Z_L8_30_v0.0_BROWSE.tiff')

    result = the_opera_treatment(test_data_input, tmp_path, 'T48SUE')

    assert result
