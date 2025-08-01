import json
import logging
import os
from json import loads
from datetime import datetime, timezone

import boto3


def handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info(f"Received event {json.dumps(event)}")

    for message in event["Records"]:
        response_topic_arn = message['messageAttributes']['response_topic_arn']['stringValue']
        message_body = loads(message["body"])
        logger.info(f"Processing message {json.dumps(message_body)}")

        response = {
            "provider": message_body["provider"],
            "collection": message_body["collection"],
            "identifier": message_body["identifier"],
            "processCompleteTime": datetime.now(timezone.utc).isoformat()[:-9] + 'Z',
            "receivedTime": datetime.now(timezone.utc).isoformat()[:-9] + 'Z',
            "submissionTime": message_body["submissionTime"],
            "response": {
                "status": "SUCCESS"
            }
        }

        client = boto3.client('sns')
        publish_response = client.publish(
            TargetArn=response_topic_arn,
            Message=json.dumps({'default': json.dumps(response)}),
            MessageStructure='json'
        )

        logger.info(f"Published response {json.dumps(response)}\n{publish_response}")
