"""Cumulus lambda class to create harmony job"""
import datetime
import logging
import os
import urllib.parse

from cumulus_logger import CumulusLogger
from cumulus_process import Process

from harmony import Collection, Request
from bignbit import utils

CUMULUS_LOGGER = CumulusLogger('submit_harmony_job')


class CMA(Process):
    """Cumulus class to submit a harmony job"""

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

        cmr_env = self.config.get('cmr_environment')
        collection_concept_id = self.config.get('collection_concept_id')
        collection_name = self.config.get('collection').get('name')
        granule = self.config.get('granule')
        if 'cmrConceptId' in granule:
            granule_concept_id = granule.get('cmrConceptId')
        else:
            granule_concept_id = urllib.parse.urlparse(granule.get('cmrLink')).path.rstrip('/').split('/')[-1].split('.')[0]
        granule_id = granule.get('granuleId')
        current_item = self.config.get('current_item')
        variable = current_item.get('id')
        big_config = self.config.get('big_config')
        bignbit_staging_bucket = self.config.get('bignbit_staging_bucket')
        harmony_staging_path = self.config.get('harmony_staging_path')

        harmony_job = submit_harmony_job(cmr_env, collection_concept_id, collection_name, granule_concept_id,
                                         granule_id, variable, big_config, bignbit_staging_bucket, harmony_staging_path)
        self.input['harmony_job'] = harmony_job
        return self.input


def submit_harmony_job(cmr_env, collection_concept_id, collection_name, granule_concept_id, granule_id, variable,
                       big_config, bignbit_staging_bucket, harmony_staging_path):
    """Generate harmony job and returns harmony job id"""

    destination_bucket_url = f's3://{bignbit_staging_bucket}/{harmony_staging_path}/{collection_name}/{datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")}'.lower()
    harmony_client = utils.get_harmony_client(cmr_env)
    harmony_request = generate_harmony_request(collection_concept_id, granule_concept_id, variable, big_config,
                                               destination_bucket_url)

    CUMULUS_LOGGER.info("Submitting Harmony request: {}", harmony_client.request_as_url(harmony_request))
    job = harmony_client.submit(harmony_request)
    harmony_job = {
        'job': job,
        'granule_id': granule_id,
        'granule_concept_id': granule_concept_id,
        'variable': variable
    }

    return harmony_job


def generate_harmony_request(collection_concept_id, granule_concept_id, variable, big_config, destination_bucket_url):
    """Generate the harmony request to be made and return request object"""

    request = Request(
        collection=Collection(id=collection_concept_id),
        granule_id=[granule_concept_id],
        variables=[variable],
        width=big_config['config']['width'],
        height=big_config['config']['height'],
        format=big_config['config'].get('format', 'image/png'),
        output_crs=big_config['config'].get('outputCrs', 'EPSG:4326'),
        destination_url=destination_bucket_url
    )
    return request


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
