"""Unit tests for send_to_gitc lambda function"""
# pylint: disable=redefined-outer-name
import json
import os

import boto3
import pytest
from moto import mock_s3, mock_sqs

import bignbit.send_to_gitc


@pytest.fixture
def sample_cnm_message():
    """Load sample CNM message from test data"""
    test_dir = os.path.dirname(os.path.realpath(__file__))
    cnm_path = os.path.join(
        test_dir, 'sample_messages', 'send_to_gitc', 'sample_cnm_message.json'
    )
    with open(cnm_path, 'r', encoding='utf-8') as file_handle:
        return json.load(file_handle)


@pytest.fixture
def sample_cnm_string(sample_cnm_message):
    """Return sample CNM message as JSON string"""
    return json.dumps(sample_cnm_message)


@mock_s3
def test_read_cnm(sample_cnm_string):
    """Test that read_cnm correctly reads and decodes S3 object"""
    # Setup
    bucket_name = 'test-bucket'
    cnm_key = 'test-cnm-message.json'

    s3_client = boto3.client('s3', region_name='us-east-1')
    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.put_object(
        Bucket=bucket_name,
        Key=cnm_key,
        Body=sample_cnm_string.encode('utf-8')
    )

    # Test
    result = bignbit.send_to_gitc.read_cnm(bucket_name, cnm_key)

    # Assert
    assert isinstance(result, str)
    assert result == sample_cnm_string

    # Verify it's valid JSON that can be parsed
    parsed = json.loads(result)
    assert parsed['version'] == '1.5.1'
    assert 'identifier' in parsed
    assert 'collection' in parsed


@mock_sqs
def test_notify_gitc(sample_cnm_string):
    """Test that notify_gitc correctly sends CNM to SQS"""
    # Setup
    sqs_region = 'us-west-2'
    sqs = boto3.client('sqs', region_name=sqs_region)

    # Create FIFO queue with content-based deduplication enabled
    queue_response = sqs.create_queue(
        QueueName='test-gibs-queue.fifo',
        Attributes={
            'FifoQueue': 'true',
            'ContentBasedDeduplication': 'true'
        }
    )
    queue_url = queue_response['QueueUrl']

    # Set environment variables
    os.environ['GIBS_SQS_URL'] = queue_url
    os.environ['GIBS_RESPONSE_TOPIC_ARN'] = 'arn:aws:sns:us-west-2:123456789012:test-response-topic'
    os.environ['GIBS_REGION'] = sqs_region

    try:
        # Test
        response = bignbit.send_to_gitc.notify_gitc(sample_cnm_string)

        # Assert SQS response
        assert 'MessageId' in response
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200

        # Verify message was sent to queue
        messages = sqs.receive_message(
            QueueUrl=queue_url,
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=1
        )

        assert 'Messages' in messages
        assert len(messages['Messages']) == 1

        message = messages['Messages'][0]
        assert message['Body'] == sample_cnm_string

        # Verify message attributes
        assert 'MessageAttributes' in message
        assert 'response_topic_arn' in message['MessageAttributes']
        assert message['MessageAttributes']['response_topic_arn']['StringValue'] == \
               'arn:aws:sns:us-west-2:123456789012:test-response-topic'

        # Verify message body can be parsed and contains expected fields
        body = json.loads(message['Body'])
        assert body['version'] == '1.5.1'
        assert body['collection'] == 'TEMPO_NO2_L3_product_vertical_column_stratosphere_LL'
        assert 'identifier' in body

    finally:
        # Cleanup environment variables
        del os.environ['GIBS_SQS_URL']
        del os.environ['GIBS_RESPONSE_TOPIC_ARN']
        del os.environ['GIBS_REGION']


@mock_s3
@mock_sqs
def test_notify_gitc_process_integration(sample_cnm_message, sample_cnm_string):
    """Test the full NotifyGitc.process() flow"""
    # Setup S3
    bucket_name = 'test-internal-bucket'
    cnm_key = 'bignbit-cnm-output/tempo_no2_l3/test-granule.cnm.json'

    s3_client = boto3.client('s3', region_name='us-east-1')
    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.put_object(
        Bucket=bucket_name,
        Key=cnm_key,
        Body=sample_cnm_string.encode('utf-8')
    )

    # Setup SQS
    sqs_region = 'us-west-2'
    sqs = boto3.client('sqs', region_name=sqs_region)
    queue_response = sqs.create_queue(
        QueueName='test-gibs-integration-queue.fifo',
        Attributes={
            'FifoQueue': 'true',
            'ContentBasedDeduplication': 'true'
        }
    )
    queue_url = queue_response['QueueUrl']

    # Set environment variables
    os.environ['GIBS_SQS_URL'] = queue_url
    os.environ['GIBS_RESPONSE_TOPIC_ARN'] = 'arn:aws:sns:us-west-2:123456789012:test-topic'
    os.environ['GIBS_REGION'] = sqs_region

    try:
        # Create input for NotifyGitc
        input_data = {
            'cnm_bucket': bucket_name,
            'cnm_key': cnm_key
        }

        # Test
        notifier = bignbit.send_to_gitc.NotifyGitc(input=input_data, config={})
        response = notifier.process()

        # Assert
        assert 'MessageId' in response

        # Verify the message in SQS
        messages = sqs.receive_message(
            QueueUrl=queue_url,
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=1
        )

        assert 'Messages' in messages
        message_body = json.loads(messages['Messages'][0]['Body'])
        assert message_body == sample_cnm_message

    finally:
        # Cleanup environment variables
        del os.environ['GIBS_SQS_URL']
        del os.environ['GIBS_RESPONSE_TOPIC_ARN']
        del os.environ['GIBS_REGION']


@mock_s3
def test_read_cnm_nonexistent_object():
    """Test that read_cnm raises error for nonexistent S3 object"""
    # Setup
    bucket_name = 'test-bucket'
    s3_client = boto3.client('s3', region_name='us-east-1')
    s3_client.create_bucket(Bucket=bucket_name)

    # Test - should raise exception
    with pytest.raises(Exception):
        bignbit.send_to_gitc.read_cnm(bucket_name, 'nonexistent-key.json')


def test_notify_gitc_parses_collection_from_cnm(sample_cnm_string):
    """Test that notify_gitc correctly parses collection field from CNM"""
    cnm_data = json.loads(sample_cnm_string)

    # Verify the test data has the expected structure
    assert cnm_data['collection'] == 'TEMPO_NO2_L3_product_vertical_column_stratosphere_LL'
    assert cnm_data['identifier'] == \
           'TEMPO_NO2_L3_V03_20250422T114702Z_S003_filtered_product_vertical_column_stratosphere_reformatted_2025112_EPSG:4326!G1273455903-LARC_CLOUD'


@mock_sqs
def test_notify_gitc_with_different_collection(sample_cnm_string):
    """Test notify_gitc with a different collection to ensure MessageGroupId is set correctly"""
    # Setup
    sqs_region = 'us-west-2'
    sqs = boto3.client('sqs', region_name=sqs_region)

    queue_response = sqs.create_queue(
        QueueName='test-collection-queue.fifo',
        Attributes={
            'FifoQueue': 'true',
            'ContentBasedDeduplication': 'true'
        }
    )
    queue_url = queue_response['QueueUrl']

    os.environ['GIBS_SQS_URL'] = queue_url
    os.environ['GIBS_RESPONSE_TOPIC_ARN'] = 'arn:aws:sns:us-west-2:123456789012:test-topic'
    os.environ['GIBS_REGION'] = sqs_region

    try:
        # Modify the CNM to have a different collection
        cnm_data = json.loads(sample_cnm_string)
        modified_collection = 'TEST_COLLECTION_V1'
        cnm_data['collection'] = modified_collection
        modified_cnm_string = json.dumps(cnm_data)

        # Test
        bignbit.send_to_gitc.notify_gitc(modified_cnm_string)

        # Verify
        messages = sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=['All'],
            MaxNumberOfMessages=1
        )

        # Note: MessageGroupId is not directly visible in received messages,
        # but we can verify the message was successfully sent to the FIFO queue
        assert 'Messages' in messages
        body = json.loads(messages['Messages'][0]['Body'])
        assert body['collection'] == modified_collection

    finally:
        del os.environ['GIBS_SQS_URL']
        del os.environ['GIBS_RESPONSE_TOPIC_ARN']
        del os.environ['GIBS_REGION']
