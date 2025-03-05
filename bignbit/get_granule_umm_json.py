"""
Simple CMA lambda that get a granule's umm-json document and ads it to the payload.
"""
import logging
import os
import urllib.parse

from cumulus_logger import CumulusLogger
from cumulus_process import Process

from bignbit import utils

CUMULUS_LOGGER = CumulusLogger('get_granule_umm_json')


class CMA(Process):
    """
    A cumulus message adapter
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self):
        """
        Download granule umm-json document

        Returns
        -------
        dict
          Same input sent to this function with a new key 'granule_umm_json' added

        """
        cmr_environment = self.config['cmr_environment']
        try:
            cmr_concept_id = self.input['granules'][0]['cmrConceptId']
        except KeyError:
            cmr_concept_id = urllib.parse.urlparse(self.input['granules'][0]['cmrLink']).path.rstrip('/').split('/')[-1]

        self.input['granule_umm_json'] = utils.get_umm_json(cmr_concept_id, cmr_environment)
        return self.input


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
