import json
import urllib.request

import jsonschema
import pytest

import bignbit.image_set
import bignbit.send_to_gitc


@pytest.fixture()
def cnm_v151_schema():
    cnm_v151_url = "https://raw.githubusercontent.com/podaac/cloud-notification-message-schema/v1.5.1/cumulus_sns_schema.json"
    cnm_schema = json.loads(urllib.request.urlopen(cnm_v151_url).read().decode("utf-8"))
    return cnm_schema


def test_get_image_sets():
    image_set_1 = bignbit.image_set.ImageSet(
        name='test_1992001',
        image={
            'name': 'test.png',
            'fileName': 'test.png',
            'type': 'browse',
            'subtype': 'png',
            "variable": "analysed_sst"
        },
        world_file={
            'name': 'test.wld',
            'fileName': 'test.wld',
            'type': 'metadata',
            'subtype': 'world file',
            "variable": "analysed_sst"
        },
        image_metadata={
            'name': 'test.xml',
            'fileName': 'test.xml',
            'type': 'metadata',
            'subtype': 'ImageMetadata-v1.2',
            'dataday': '1992001',
            "variable": "analysed_sst"
        })

    image_set_2 = bignbit.image_set.ImageSet(
        name='test2_1992002',
        image={
            'name': 'test2.png',
            'fileName': 'test2.png',
            'type': 'browse',
            'subtype': 'png',
            "variable": "analysed_sst"
        },
        world_file={
            'name': 'test2.wld',
            'fileName': 'test2.wld',
            'type': 'metadata',
            'subtype': 'world file',
            "variable": "analysed_sst"
        },
        image_metadata={
            'name': 'test2.xml',
            'fileName': 'test2.xml',
            'type': 'metadata',
            'subtype': 'ImageMetadata-v1.2',
            'dataday': '1992002',
            "variable": "analysed_sst"
        })
    test_input = [
        image_set_1.image, image_set_1.image_metadata, image_set_1.world_file,
        image_set_2.image, image_set_2.image_metadata, image_set_2.world_file,
    ]

    image_sets = bignbit.image_set.from_big_output(test_input)

    assert len(image_sets) == 2
    assert image_set_1 in image_sets
    assert image_set_2 in image_sets


def test_construct_cnm(cnm_v151_schema):
    image_set_1 = bignbit.image_set.ImageSet(
        name='test_1992001',
        image={
            'name': 'test.png',
            'fileName': 's3://test.png',
            'type': 'browse',
            'size': 512,
            'subtype': 'png',
            'key': 'test.png',
            'bucket': 'test',
            "variable": "analysed_sst"
        },
        world_file={
            'name': 'test.wld',
            'fileName': 's3://test.wld',
            'type': 'metadata',
            'size': 25,
            'subtype': 'world file',
            'key': 'test.png',
            'bucket': 'test',
            "variable": "analysed_sst"
        },
        image_metadata={
            'name': 'test.xml',
            'fileName': 's3://test.xml',
            'type': 'metadata',
            'size': 30,
            'subtype': 'ImageMetadata-v1.2',
            'dataday': '1992001',
            'key': 'test.xml',
            'bucket': 'test',
            "variable": "analysed_sst"
        })

    test_input = [
        image_set_1.image, image_set_1.image_metadata, image_set_1.world_file
    ]

    image_sets = bignbit.image_set.from_big_output(test_input)

    cnm = bignbit.send_to_gitc.construct_cnm(image_sets[0], 'pytest', 'token', 'testcollection')
    jsonschema.validate(cnm, cnm_v151_schema, format_checker=jsonschema.FormatChecker())


def test_construct_cnm_no_wld(cnm_v151_schema):
    test_input = [
        {
            'name': 'test.png',
            'fileName': 's3://test.png',
            'type': 'browse',
            'size': 512,
            'subtype': 'png',
            'key': 'test.png',
            'bucket': 'test',
            "variable": "analysed_sst"
        },
        {
            'name': 'test.xml',
            'fileName': 's3://test.xml',
            'type': 'metadata',
            'size': 30,
            'subtype': 'ImageMetadata-v1.2',
            'dataday': '1992001',
            'key': 'test.xml',
            'bucket': 'test',
            "variable": "analysed_sst"
        }
    ]

    image_sets = bignbit.image_set.from_big_output(test_input)

    cnm = bignbit.send_to_gitc.construct_cnm(image_sets[0], 'pytest', 'token', 'testcollection')
    jsonschema.validate(cnm, cnm_v151_schema, format_checker=jsonschema.FormatChecker())

def test_construct_cnm_variable_with_slash(cnm_v151_schema):
    test_input = [
        {
            'name': 'test.png',
            'fileName': 's3://test.png',
            'type': 'browse',
            'size': 512,
            'subtype': 'png',
            'key': 'test.png',
            'bucket': 'test',
            "variable": "groupA/analysed_sst"
        },
        {
            'name': 'test.xml',
            'fileName': 's3://test.xml',
            'type': 'metadata',
            'size': 30,
            'subtype': 'ImageMetadata-v1.2',
            'dataday': '1992001',
            'key': 'test.xml',
            'bucket': 'test',
            "variable": "groupA/analysed_sst"
        }
    ]

    image_sets = bignbit.image_set.from_big_output(test_input)

    cnm = bignbit.send_to_gitc.construct_cnm(image_sets[0], 'pytest', 'token', 'testcollection')
    jsonschema.validate(cnm, cnm_v151_schema, format_checker=jsonschema.FormatChecker())
    assert cnm['collection'] == 'testcollection_groupA_analysed_sst'