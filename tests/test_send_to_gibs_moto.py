"""
==============
test_send_to_gibs_moto.py
==============
Uses moto to mock out the AWS resources in use and send a few sample messages to a fake GIBS implementation.
"""
import json
import os
import threading
import urllib.request
import uuid

import boto3
import jsonschema
import moto
import pytest

import mock_gitc
import bignbit.build_image_sets
import bignbit.send_to_gitc

FAKE_GIBS_QUEUE_NAME = "PODAAC_Sandbox_Test_IN.fifo"
FAKE_GIBS_REGION = "us-east-1"

FAKE_RESPONSE_QUEUE_NAME = "svc-pobit-test-gibs-response-queue"


@pytest.fixture()
def cma_schema():
    cma_schema_url = "https://raw.githubusercontent.com/nasa/cumulus/master/packages/schemas/files.schema.json"
    cma_schema = json.loads(urllib.request.urlopen(cma_schema_url).read().decode("utf-8"))
    return cma_schema


@pytest.fixture()
def cnm_v151_schema():
    cnm_v151_url = \
        "https://raw.githubusercontent.com/podaac/cloud-notification-message-schema/v1.5.1/cumulus_sns_schema.json"
    cnm_schema = json.loads(urllib.request.urlopen(cnm_v151_url).read().decode("utf-8"))
    return cnm_schema


@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'testing')
    monkeypatch.setenv('AWS_SECURITY_TOKEN', 'testing')
    monkeypatch.setenv('AWS_SESSION_TOKEN', 'testing')
    with moto.mock_sqs():
        with moto.mock_sns():
            yield


@pytest.fixture()
def fake_gibs_sqs_queue(monkeypatch):
    mock_gibs_sqs_resource = boto3.resource('sqs', region_name=FAKE_GIBS_REGION)
    gibs_sqs_queue = mock_gibs_sqs_resource.create_queue(
        QueueName=FAKE_GIBS_QUEUE_NAME,
        Attributes={"FifoQueue": "true"}
    )
    monkeypatch.setenv(bignbit.send_to_gitc.GIBS_REGION_ENV_NAME, FAKE_GIBS_REGION)
    monkeypatch.setenv(bignbit.send_to_gitc.GIBS_SQS_URL_ENV_NAME, gibs_sqs_queue.url)
    yield gibs_sqs_queue


@pytest.fixture()
def fake_response_sqs_queue(monkeypatch):
    mock_sqs_resource = boto3.resource('sqs', region_name='us-west-2')
    response_sqs_queue = mock_sqs_resource.create_queue(
        QueueName=FAKE_RESPONSE_QUEUE_NAME
    )
    yield response_sqs_queue


@pytest.fixture()
def fake_response_sns_topic(fake_response_sqs_queue):
    mock_sns_resource = boto3.resource('sns', region_name='us-west-2')
    topic = mock_sns_resource.create_topic(Name='gitcresponses')
    topic.subscribe(
        Protocol='sqs',
        Endpoint=fake_response_sqs_queue.attributes['QueueArn'],
        Attributes={
            'RawMessageDelivery': 'true'
        }
    )
    return topic


@pytest.fixture()
def mock_gitc_success(fake_gibs_sqs_queue, fake_response_sns_topic) -> mock_gitc.GITC:
    gitc = mock_gitc.GITC(fake_gibs_sqs_queue, fake_response_sns_topic)
    with gitc as mock:
        thread = threading.Thread(target=mock.process_messages)
        thread.daemon = True
        thread.start()
        yield mock


def test_process_sends_message(fake_response_sqs_queue, mock_gitc_success, cnm_v151_schema, monkeypatch):
    test_dir = os.path.dirname(os.path.realpath(__file__))
    event = json.load(
        open(os.path.join(test_dir, 'messages', 'MUR-JPL-L4-GLOB-v4.1', 'mur_message_in.json')))

    event['cma']['event'] = bignbit.build_image_sets.lambda_handler(event, {})
    for imageset in event['cma']['event']['payload']['pobit']:
        sub_event = event.copy()
        del sub_event['cma']['event']['payload']['pobit']
        sub_event['cma']['event']['payload'] = imageset
        sub_event['cma']['task_config']['token'] = str(uuid.uuid4())
        bignbit.send_to_gitc.lambda_handler(sub_event, {})

    sent_messages = mock_gitc_success.wait_for_messages(count=1)

    assert len(sent_messages) == 1

    gibs_cnm = sent_messages[0]
    jsonschema.validate(gibs_cnm, cnm_v151_schema, format_checker=jsonschema.FormatChecker())

    response_messages = fake_response_sqs_queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=5)
    gitc_cnmr = json.loads(response_messages[0].body)

    assert gitc_cnmr['response']['status'] == "SUCCESS"
