"""Cumulus lambda class to create harmony job"""

import logging
import os
from cumulus_logger import CumulusLogger
from cumulus_process import Process

from harmony import BBox, Collection, Request
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

        harmony_job = create_harmony_job(self.config)
        self.input['harmony_job'] = harmony_job
        return self.input


def create_harmony_job(config):
    """Generate harmony job and returns harmony job id"""

    cmr_env = config.get('cmr_environment')
    collection_concept_id = config.get('collection_concept_id')
    granule = config.get('granule')
    granule_concept_id = granule.get('cmrConceptId')
    granule_id = granule.get('granuleId')
    current_item = config.get('current_item')
    variable = current_item.get('id')
    big_config = config.get('big_config')

    files = granule.get('files')
    bucket_name = None
    for file in files:
        if file.get('type') == 'data':
            file_path = os.path.dirname(file.get('key'))
            destination_bucket_url = f's3://{file.get('bucket')}/{file_path}'

    harmony_client = utils.get_harmony_client(cmr_env)
    harmony_request = generate_harmony_request(collection_concept_id, granule_concept_id, variable, big_config, destination_bucket_url)

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
        spatial=BBox(-180, -90, 180, 90),
        width=big_config['config']['width'],
        height=big_config['config']['height'],
        format="image/png",
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

    CUMULUS_LOGGER.info(event)
    return CMA.cumulus_handler(event, context=context)


if __name__ == "__main__":
    CMA()
