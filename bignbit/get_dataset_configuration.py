"""
Simple CMA lambda that gets the dataset configuration associated with the collection being processed
"""
import json
import logging
import os

import boto3
from cumulus_logger import CumulusLogger
from cumulus_process import Process

CUMULUS_LOGGER = CumulusLogger('get_dataset_configuration')


class MissingDatasetConfiguration(Exception):
    """
    Exception for missing dataset configuration
    """


class CMA(Process):
    """
    A cumulus message adapter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self):
        """
        Download dataset configuration file from s3

        Returns
        -------
        dict
          Same input sent to this function with a new key 'datasetConfigurationForBIG' added

        """
        config_bucket_name = self.config['config_bucket_name']
        config_key_name = self.config['config_key_name']

        self.input['datasetConfigurationForBIG'] = {}
        self.input['datasetConfigurationForBIG']['config'] = get_collection_config(config_bucket_name, config_key_name)
        return self.input


def get_collection_config(config_bucket_name: str, config_key_name: str) -> dict:
    """
    Retrieve the dataset configuration from the given s3 bucket and key

    Parameters
    ----------
    config_bucket_name: str
      Bucket name containing the configuration

    config_key_name: str
      Key to object storing configuration

    Returns
    -------
    dict
      The configuration json document as a dict
    """
    s3_client = boto3.client('s3')

    try:
        object_result = s3_client.get_object(Bucket=config_bucket_name, Key=config_key_name)
    except s3_client.client.exceptions.NoSuchKey as ex:
        raise MissingDatasetConfiguration(
            f"Dataset configuration not found s3://{config_bucket_name}/{config_key_name}") from ex

    return json.load(object_result['Body'])


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
