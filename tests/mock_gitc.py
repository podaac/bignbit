import json
from datetime import datetime, timezone
from time import sleep
from typing import Dict, List

from moto import sqs


class GITC:
    def __init__(self, incoming_queue, outgoing_topic):
        self._incoming_queue = incoming_queue
        self._outgoing_topic = outgoing_topic
        self._received_messages = []

    def __enter__(self):
        self._incoming_queue.load()
        self._outgoing_topic.load()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._incoming_queue.purge()

    def wait_for_messages(self, count: int = 1) -> List[sqs.models.Message]:
        while len(self._received_messages) < count:
            sleep(1)
        return self._received_messages[0:count]

    def process_messages(self):
        while True:
            messages = self._incoming_queue.receive_messages(WaitTimeSeconds=10, MessageAttributeNames=["All"])
            for message in messages:
                message_body = json.loads(message.body)
                self._received_messages.append(message)

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

                self._outgoing_topic.publish(Message=json.dumps(response))
