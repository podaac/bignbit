"""
Simple CMA lambda that get a granule's umm-json document and ads it to the payload.
"""
import logging
import os

import requests
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
        cmr_link = self.input['granules'][0]['cmrLink']

        self.input['granule_umm_json'] = download_umm_json(cmr_link, cmr_environment)
        return self.input


def download_umm_json(cmr_link: str, cmr_environment: str) -> dict:
    """
    Retrieve the umm-json document from the given cmr_link

    Parameters
    ----------
    cmr_link: str
      Link to the umm-g for downloading

    cmr_environment: str
      CMR environment used to retrieve user token

    Returns
    -------
    dict
      The umm-json document
    """
    edl_user, edl_pass = utils.get_edl_creds()
    token = utils.get_cmr_user_token(edl_user, edl_pass, cmr_environment)

    umm_json_response = requests.get(cmr_link, headers={'Authorization': f'Bearer {token}'}, timeout=10)
    umm_json_response.raise_for_status()
    umm_json = umm_json_response.json()

    return umm_json


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
