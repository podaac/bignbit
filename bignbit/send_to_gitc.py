"""lambda function used to send CNM to GIBS"""

import json
import logging
import os
from typing import Any

import boto3
from cumulus_logger import CumulusLogger
from cumulus_process import Process

CUMULUS_LOGGER = CumulusLogger('send_to_gitc')

GIBS_REGION_ENV_NAME = "GIBS_REGION"
GIBS_SQS_URL_ENV_NAME = "GIBS_SQS_URL"
GIBS_RESPONSE_TOPIC_ARN_ENV_NAME = "GIBS_RESPONSE_TOPIC_ARN"

GIBS_CRS_NAME_TO_SUFFIX = {
    'EPSG:4326': 'LL',
    'EPSG:3413': 'N',
    'EPSG:3031': 'S'
}


class NotifyGitc(Process):
    """
    Class for notifying GITC (via SQS) that a Browse Image is ready to transfer

    Attributes
    ----------
    logger: logger
        cumulus logger
    config: dictionary
        configuration from cumulus
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self):
        """
        Main process to send daily Browse Image data to GIBS

        Returns
        ----------
        dict
            Payload that is returned to the cma which is a dictionary with \
            list of granules
        """

        # Send ImageSet(s) to GITC for processing
        cnm_bucket = self.input.get('cnm_bucket', '')
        cnm_key = self.input.get('cnm_key', '')

        cnm_payload = read_cnm(cnm_bucket, cnm_key)
        sqs_response = notify_gitc(cnm_payload)

        return sqs_response


def read_cnm(cnm_bucket: str, cnm_key: str) -> str:
    """
    Downloads and reads CNM message from S3 so it can be serialized into
    SQS message

    Parameters
    ----------
    cnm_bucket: str
      S3 bucket containing the CNM (usually *-internal)
    cnm_key: str
      Key within the bucket pointing to CNM JSON
    """
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=cnm_bucket, Key=cnm_key)
    return response['Body'].read().decode('utf-8')


def notify_gitc(cnm_payload: str) -> dict[str, Any]:
    """
    Builds and sends a CNM message to GITC

    Parameters
    ----------
    cnm_payload: str
      string containing contents of CNM JSON

    Returns
    -------
    sqs_response: dict[str, Any]
      Response from GIBS SQS
    """
    cnm = json.loads(cnm_payload)
    queue_url = os.environ.get(GIBS_SQS_URL_ENV_NAME)
    gibs_response_topic_arn = os.environ.get(GIBS_RESPONSE_TOPIC_ARN_ENV_NAME)
    gibs_region = os.environ.get(GIBS_REGION_ENV_NAME)
    CUMULUS_LOGGER.info(f"Sending SQS message to GITC for image {cnm['identifier']}")

    sqs_message_params = {
        "QueueUrl": queue_url,
        "MessageBody": cnm_payload,
        "MessageGroupId": cnm['collection'],
        "MessageAttributes": {
            'response_topic_arn': {
                'StringValue': gibs_response_topic_arn,
                'DataType': 'String'
            }
        }
    }
    CUMULUS_LOGGER.debug(f'CNM message for GIBS: {sqs_message_params}')

    sqs = boto3.client('sqs', region_name=gibs_region)
    response = sqs.send_message(**sqs_message_params)

    CUMULUS_LOGGER.debug(f'SQS send_message output: {response}')

    return response


def lambda_handler(event, context):
    """handler that gets called by aws lambda
    Parameters
    ----------
    event: dictionary
        event from a lambda call
    context: dictionary
        context from a lambda call
    Returns
    ----------
        dict
            A CMA json message
    """
    # pylint: disable=duplicate-code
    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }

    logging_level = os.environ.get('LOGGING_LEVEL', 'info')
    CUMULUS_LOGGER.logger.setLevel(levels.get(logging_level, 'info'))
    CUMULUS_LOGGER.setMetadata(event, context)

    return NotifyGitc.cumulus_handler(event, context=context)


if __name__ == "__main__":
    NotifyGitc()
