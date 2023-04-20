"""lambda function that stores the CMA message into a s3 bucket"""
import json
import logging
import os

import boto3
from cumulus_logger import CumulusLogger
from cumulus_process import Process

CUMULUS_LOGGER = CumulusLogger('save_cma_message')


class CMA(Process):
    """
    A cumulus message adapter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self):
        """
        Upload CMA message into a s3 bucket

        Returns
        -------
        dict
          Same input sent to this function

        """
        pobit_audit_bucket = self.config['pobit_audit_bucket']
        cma_key_name = self.config['cma_key_name']

        upload_cma(pobit_audit_bucket, cma_key_name, self.input)

        return self.input


def upload_cma(pobit_audit_bucket: str, cma_key_name: str, cma_content: dict):
    """
    Upload CMA message into a s3 bucket

    Parameters
    ----------
    pobit_audit_bucket: str
      Bucket name containing where CMA should be uploaded

    cma_key_name: str
      Key to object location in bucket

    cma_content: dict
      The CMA message to upload

    Returns
    -------
    None
    """
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Body=json.dumps(cma_content, default=str).encode("utf-8"),
        Bucket=pobit_audit_bucket,
        Key=cma_key_name
    )


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
    CUMULUS_LOGGER.logger.level = levels.get(logging_level, 'info')
    CUMULUS_LOGGER.setMetadata(event, context)

    return CMA.cumulus_handler(event, context=context)


if __name__ == "__main__":
    CMA()
