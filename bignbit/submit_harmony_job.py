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
        current_variable = self.config.get('current_variable')
        variable = current_variable.get('id')
        current_crs = self.config.get('current_crs')
        big_config = self.config.get('big_config')
        output_width, output_height = determine_output_dimensions(big_config, current_crs)
        bignbit_staging_bucket = self.config.get('bignbit_staging_bucket')
        harmony_staging_path = self.config.get('harmony_staging_path')

        harmony_job = submit_harmony_job(cmr_env, collection_concept_id, collection_name, granule_concept_id,
                                         granule_id, variable, output_width, output_height, current_crs, big_config,
                                         bignbit_staging_bucket, harmony_staging_path)
        self.input['harmony_job'] = harmony_job
        return self.input


def submit_harmony_job(cmr_env, collection_concept_id, collection_name, granule_concept_id, granule_id, variable,
                       output_width, output_height, output_crs, big_config, bignbit_staging_bucket, harmony_staging_path):
    """Generate harmony job and returns harmony job id"""

    destination_bucket_url = f's3://{bignbit_staging_bucket}/{harmony_staging_path}/{collection_name}/{datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")}'.lower()
    harmony_client = utils.get_harmony_client(cmr_env)
    harmony_request = generate_harmony_request(collection_concept_id, granule_concept_id, variable, output_width, output_height, output_crs,
                                               big_config, destination_bucket_url)

    CUMULUS_LOGGER.info("Submitting Harmony request: {}", harmony_client.request_as_url(harmony_request))
    job = harmony_client.submit(harmony_request)
    harmony_job = {
        'job': job,
        'granule_id': granule_id,
        'granule_concept_id': granule_concept_id,
        'variable': variable,
        'output_crs': output_crs,
    }

    return harmony_job


def determine_output_dimensions(big_config, output_crs):
    """Set the output width and height of the browse image based on config and projection."""
    big_width = big_config['config'].get('width')
    big_height = big_config['config'].get('height')
    if not big_width or not big_height:
        return big_width, big_height

    if output_crs.upper() == "EPSG:4326":
        if big_width == big_height or big_width < big_height:
            output_width = 2 * big_height
        else:
            output_width = big_width
        output_height = big_height
    else:
        output_width = min(big_width, big_height)
        output_height = min(big_width, big_height)
    return (output_width, output_height)


def generate_harmony_request(collection_concept_id, granule_concept_id, variable, output_width, output_height, output_crs, big_config, destination_bucket_url):
    """Generate the harmony request to be made and return request object"""

    kwargs = {
        'collection': Collection(id=collection_concept_id),
        'granule_id': [granule_concept_id],
        'variables': [variable],
        'format': big_config['config'].get('format', 'image/png'),
        'destination_url': destination_bucket_url
    }
    # Workaround to prevent sending harmony requests that are
    # equirectangular projection through the reproject service.
    # Avoids unnecessary processing and errors for some collections
    # that do not support reprojection.
    if output_crs.upper() != 'EPSG:4326':
        kwargs['crs'] = output_crs
        # Use the scaleExtent either from datasetConfig or use the
        # default values from GIBS
        if output_crs.upper() == "EPSG:3413" or output_crs.upper() == "EPSG:3031":
            kwargs['scale_extent'] = big_config['config'].get(
                'scaleExtentPolar',
                [-4194303, -4194303, 419303, 419303]
            )
    if output_height and output_width:
        kwargs['height'] = output_height
        kwargs['width'] = output_width

    request = Request(**kwargs)
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
