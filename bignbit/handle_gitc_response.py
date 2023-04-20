"""lambda function used to be triggered when receiving data from GITC"""
import json
import logging
import os
from json import loads
import boto3
from botocore.exceptions import ClientError


def handler(event, _):
    """
    Handler of the function

    Parameters
    ----------
    event: dictionary

    Returns
    ----------
    Status: dictionary

    """
    logger = logging.getLogger('handle_gitc_response')
    levels = {
        'critical': logging.CRITICAL, 'error': logging.ERROR,
        'warn': logging.WARNING, 'warning': logging.WARNING,
        'info': logging.INFO, 'debug': logging.DEBUG
    }
    logger.setLevel(levels.get(os.environ.get('LOGGING_LEVEL', 'info')))

    logger.debug("Processing event %s", json.dumps(event))

    for message in event["Records"]:
        message_body = loads(message["body"])
        task_token = message_body["identifier"]
        client = boto3.client('stepfunctions')
        try:
            client.send_task_success(taskToken=task_token, output=json.dumps(message_body))
            logger.info("Step function triggered for task token %s", task_token)
        except ClientError:
            logger.warning("Error sending task success for messageId %s task token %s",
                           message['messageId'], task_token,
                           exc_info=True)
    return {"statusCode": 200, "body": "All good"}
