
import json
import os
import pytest

import bignbit.image_set

@pytest.fixture()
def opera_cnm_message():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    cma_json = json.load(open(os.path.join(
        test_dir, 'sample_messages', 'build_image_sets',
        'cma.sit.workflow-input.OPERA_L3_DSWx-HLS_mock.json')))
    return cma_json["payload"]["big"]

@pytest.fixture()
def tempo_cnm_message():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    cma_json = json.load(open(os.path.join(
        test_dir, 'sample_messages', 'build_image_sets',
        'cma.sit.workflow-input.TEMPO_O3TOT_L2_V04_mock.json')))
    return cma_json["payload"]["big"]


def test_build_image_sets_nocrs(opera_cnm_message):
    image_sets = bignbit.image_set.from_big_output(opera_cnm_message)

    expected_image_set = bignbit.image_set.ImageSet(
        name="OPERA_L3_DSWx-HLS_T32VMJ_167131_20250920T103741Z_20250922T082308Z_S2A_30_v1.0_BROWSE_2025263",
        image={
            "fileName": "OPERA_L3_DSWx-HLS_T32VMJ_167131_20250920T103741Z_20250922T082308Z_S2A_30_v1.0_BROWSE.tif",
            "bucket": "svc-bignbit-podaac-sit-svc-staging",
            "key": "opera_hls_processing/20260105/OPERA_L3_DSWx-HLS_T32VMJ_167131_20250920T103741Z_20250922T082308Z_S2A_30_v1.0_BROWSE.tif",
            "local_filepath": "/tmp/tmpva4cvydi/OPERA_L3_DSWx-HLS_T32VMJ_20250920T103741Z_20250922T082308Z_S2A_30_v1.0_BROWSE/167131/OPERA_L3_DSWx-HLS_T32VMJ_167131_20250920T103741Z_20250922T082308Z_S2A_30_v1.0_BROWSE.tif",
            "checksum": "19e9802c817c862c0689f9039847459eb1127ca92d9e0105761326cdea2bf5037a96dd4b5f835611f065e3389b6c57ced67472af6fb49745714a739360650251",
            "checksumType": "SHA512",
            "type": "browse",
            "subtype": "geotiff",
            "variable": "none",
            "dataday": "2025263"
        },
        image_metadata={
            "fileName": "OPERA_L3_DSWx-HLS_T32VMJ_167131_20250920T103741Z_20250922T082308Z_S2A_30_v1.0_BROWSE.xml",
            "bucket": "svc-bignbit-podaac-sit-svc-staging",
            "key": "opera_hls_processing/20260105/OPERA_L3_DSWx-HLS_T32VMJ_167131_20250920T103741Z_20250922T082308Z_S2A_30_v1.0_BROWSE.xml",
            "local_filepath": "/tmp/tmpva4cvydi/OPERA_L3_DSWx-HLS_T32VMJ_20250920T103741Z_20250922T082308Z_S2A_30_v1.0_BROWSE/167131/OPERA_L3_DSWx-HLS_T32VMJ_167131_20250920T103741Z_20250922T082308Z_S2A_30_v1.0_BROWSE.tif",
            "checksum": "633cc1372a65545b945b29813852888e7632c79a92a6e0dafc86691900b8c0b52caa1b4532e5a9d15accbe5a0a3c57a4b05cd2c8dead1217c3fc6e481dfda446",
            "checksumType": "SHA512",
            "type": "metadata",
            "subtype": "ImageMetadata-v1.2",
            "variable": "none",
            "dataday": "2025263",
            "size": 364
        },
        world_file={}
    )
    assert expected_image_set in image_sets


def test_build_image_sets_with_crs(tempo_cnm_message):
    image_sets = bignbit.image_set.from_big_output(tempo_cnm_message)

    expected_image_set = bignbit.image_set.ImageSet(
        name="TEMPO_O3TOT_L2_V04_20250913T000441Z_S015G04_regridded_filtered_product_column_amount_o3_reformatted_2025256_EPSG:4326",
        image={
            "fileName": "TEMPO_O3TOT_L2_V04_20250913T000441Z_S015G04_regridded_filtered_product_column_amount_o3_reformatted.png",
            "bucket": "svc-bignbit-podaac-sit-svc-staging",
            "key": "bignbit-harmony-output/tempo_o3tot_l2/20260105/2db6248f-bfde-4f82-bd1b-9a48ab6966e9/8903857/TEMPO_O3TOT_L2_V04_20250913T000441Z_S015G04_regridded_filtered_product_column_amount_o3_reformatted.png",
            "checksum": "2ce4415ffe390a4602a52a230a7bb246",
            "checksumType": "md5",
            "variable": "product/column_amount_o3",
            "output_crs": "EPSG:4326",
            "type": "browse",
            "subtype": "png",
            "dataday": "2025256"
        },
        image_metadata={
            "fileName": "TEMPO_O3TOT_L2_V04_20250913T000441Z_S015G04_regridded_filtered_product_column_amount_o3_reformatted.xml",
            "bucket": "svc-bignbit-podaac-sit-svc-staging",
            "key": "bignbit-harmony-output/tempo_o3tot_l2/20260105/2db6248f-bfde-4f82-bd1b-9a48ab6966e9/8903857/TEMPO_O3TOT_L2_V04_20250913T000441Z_S015G04_regridded_filtered_product_column_amount_o3_reformatted.xml",
            "checksum": "ff3ced6491e8efff03db6194c12c60dbfa1edcf23b0734f02f7b4e7306d45831326ad7e4a4d2f824d7712632dfdb249d8b9289c9307f916868f8dc31f22f5bf8",
            "checksumType": "SHA512",
            "variable": "product/column_amount_o3",
            "output_crs": "EPSG:4326",
            "type": "metadata",
            "subtype": "ImageMetadata-v1.2",
            "dataday": "2025256",
            "size": 365
        },
        world_file={
            "fileName": "TEMPO_O3TOT_L2_V04_20250913T000441Z_S015G04_regridded_filtered_product_column_amount_o3_reformatted.pgw",
            "bucket": "svc-bignbit-podaac-sit-svc-staging",
            "key": "bignbit-harmony-output/tempo_o3tot_l2/20260105/2db6248f-bfde-4f82-bd1b-9a48ab6966e9/8903857/TEMPO_O3TOT_L2_V04_20250913T000441Z_S015G04_regridded_filtered_product_column_amount_o3_reformatted.pgw",
            "checksum": "9c046aae31658304a52445711972c854",
            "checksumType": "md5",
            "variable": "product/column_amount_o3",
            "output_crs": "EPSG:4326",
            "type": "metadata",
            "subtype": "world file",
            "dataday": "2025256"
        }
    )
    assert expected_image_set in image_sets