import pytest
from bignbit.get_collection_concept_id import get_collection_concept_id


@pytest.fixture(scope="session")
def vcr_config():
    return {"filter_headers": ["authorization"], "decode_compressed_response": True}

@pytest.mark.vcr
@pytest.mark.parametrize("collection_shortname, collection_version, collection_provider, expected_concept_id", [
    ("PREFIRE_SAT2_2B-FLX_COG", "R01", "LARC_CLOUD", "C1273150419-LARC_CLOUD"),
    ("MUR-JPL-L4-GLOB-v4.1", "4.1", "POCLOUD", "C1238621141-POCLOUD")
], ids=["PREFIRE_SAT2_2B-FLX_COG", "MUR-JPL-L4-GLOB-v4.1"])
def test_get_collection_concept_id(collection_shortname, collection_version, collection_provider, expected_concept_id, monkeypatch):

    monkeypatch.setattr('bignbit.utils.get_edl_creds', lambda: (None, None))
    monkeypatch.setattr('bignbit.utils.get_cmr_user_token', lambda *args: None)

    concept_id = get_collection_concept_id(collection_shortname, collection_version, collection_provider, "UAT")

    assert expected_concept_id == concept_id