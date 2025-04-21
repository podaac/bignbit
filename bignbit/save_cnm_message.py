"""lambda function that stores the CMA message into a s3 bucket"""
import json
import logging
import os

import boto3
from cumulus_logger import CumulusLogger
from cumulus_process import Process

from bignbit import utils

CUMULUS_LOGGER = CumulusLogger('save_cmm_message')


class CMA(Process):
    """
    A cumulus message adapter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self):
        """
        Upload CNM message into a s3 bucket

        Returns
        -------
        str
          Path to the object in s3

        """
        bignbit_audit_bucket = self.config['bignbit_audit_bucket']
        bignbit_audit_path = self.config['bignbit_audit_path']

        granule_ur = self.config['granule_ur']

        cnm_content = self.config['cnm']
        collection_name = cnm_content['collection']

        cnm_object_path = upload_cnm(bignbit_audit_bucket, bignbit_audit_path, collection_name, granule_ur, cnm_content)

        return cnm_object_path


def upload_cnm(bignbit_audit_bucket: str, bignbit_audit_path: str, collection_name: str, granule_ur : str, cnm_content: dict):
    """
    Upload CNM message into a s3 bucket

    Parameters
    ----------
    bignbit_audit_bucket: str
        bucket name where the CNM message will be stored
    bignbit_audit_path: str
        path where the CNM message will be stored
    collection_name: str
        name of the collection
    granule_ur : str
        granule unique identifier
    cnm_content: dict
        CNM content as a python dictionary

    Returns
    ----------
        str
            The path to the uploaded CNM message in s3
    """

    cnm_key_name = bignbit_audit_path + "/" + collection_name + "/" + granule_ur + "." + cnm_content[
        'submissionTime'] + "." + "cnm.json"
    cnm_content_json = json.dumps(cnm_content)

    return utils.upload_string_as_object(bignbit_audit_bucket, cnm_key_name, cnm_content_json)


def lambda_handler(event, context):
    """
    Main lambda handler that gets called by aws lambda
    Parameters
    ----------
    event: dictionary
        event from a lambda call
    context: dictionary
        context from a lambda call
    Returns
    ----------
        dict
            A CNM json message
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
