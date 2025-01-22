"""Cumulus lambda class to extract details about the results from the Harmony job"""
import hashlib
import logging
import os
from urllib.parse import urlparse

import boto3
from cumulus_logger import CumulusLogger
from cumulus_process import Process
from harmony import LinkType

from bignbit import utils

CUMULUS_LOGGER = CumulusLogger('process_harmony_results')


class CMA(Process):
    """Cumulus class to read the output from a harmony job"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self):
        """
        1. Build harmony request for input variable, collection concept id, and granule concept id
        2. Submit request
        3. Put harmony job id into the output payload

        Returns
        ----------
        CMA message
        """

        harmony_job = self.config.get("harmony_job")
        cmr_env = self.config.get("cmr_environment")
        variable = self.config.get("variable")

        return process_results(harmony_job, cmr_env, variable)


def process_results(harmony_job_id: str, cmr_env: str, variable: str):
    """
    Process the results of a Harmony job

    Parameters
    ----------
    harmony_job_id : str
       The ID of the Harmony job to process
    cmr_env : str
       The CMR environment to use
    variable : str
        The variable being processed

    Returns
    ----------
        dict
            A list of CMA file dictionaries pointing to the transformed image(s)
    """
    s3_client = boto3.client('s3')
    harmony_client = utils.get_harmony_client(cmr_env)
    result_urls = list(harmony_client.result_urls(harmony_job_id, link_type=LinkType.s3))

    CUMULUS_LOGGER.info("Processing {} result files for {}", len(result_urls), variable)
    CUMULUS_LOGGER.debug("Results: {}", result_urls)

    file_dicts = []
    for url in result_urls:
        bucket, key = urlparse(url).netloc, urlparse(url).path.lstrip("/")

        response = s3_client.get_object(Bucket=bucket, Key=key)
        md5_hash = hashlib.new('md5')
        for chunk in response['Body'].iter_chunks(chunk_size=1024 * 1024):
            md5_hash.update(chunk)

        filename = key.split("/")[-1]
        file_dict = {
            "fileName": filename,
            "bucket": bucket,
            "key": key,
            "checksum": md5_hash.hexdigest(),
            "checksumType": 'md5'
        }
        # Weird quirk where if we are working with a collection that doesn't define variables, the Harmony request
        # should specify 'all' as the variable value but the GIBS message should be sent with the variable set to 'none'
        if variable.lower() != 'all':
            file_dict['variable'] = variable
        file_dicts.append(file_dict)

    return file_dicts


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
