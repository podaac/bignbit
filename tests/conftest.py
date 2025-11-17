import pytest


@pytest.fixture(scope="session")
def vcr_config():
    return {"filter_headers": ["authorization"], "decode_compressed_response": True, "record_mode": "once"}