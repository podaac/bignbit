"""lambda function used to be triggered when receiving data from GITC"""
import json
import logging
import os
from json import loads
from datetime import datetime, timezone
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
        gitc_id = message_body["identifier"]
        collection = message_body["collection"]
        cma_key = "{}/{}/{}.{}.cma.json"

        received_time = datetime.now(timezone.utc).isoformat()[:-9] + 'Z'

        client = boto3.client('lambda')

        cma_event = ('{"pobit_audit_bucket": "' + os.environ['POBIT_AUDIT_BUCKET_NAME']
                     + '", "cma_key_name": "' + cma_key.format(os.environ['POBIT_AUDIT_PATH_NAME'], collection, gitc_id, received_time)
                     + '", "cma_content": ' + json.dumps(message_body) + '}')

        try:
            client.invoke(
                FunctionName=os.environ['SAVE_CMA_LAMBDA_FUNCTION_NAME'],
                InvocationType='Event',
                Payload=cma_event)
            logger.info("Save CMA message lambda invoked for id %s", gitc_id)
        except ClientError:
            logger.warning("Error invoking save cma lambda for messageId %s gitcID %s",
                           message['messageId'], gitc_id,
                           exc_info=True)
    return {"statusCode": 200, "body": "All good"}
