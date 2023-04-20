"""Cumulus lambda class to check harmony job status"""

import logging
import os
from cumulus_logger import CumulusLogger
from cumulus_process import Process

from bignbit import utils

CUMULUS_LOGGER = CumulusLogger('get_harmony_job_status')


class CMA(Process):
    """Cumulus class to check harmony job status"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self):
        """
        Checks the job status of a harmony call

        Returns
        ----------
        CMA message
        """

        job_status = check_harmony_job(self.config)
        self.input['harmony_job_status'] = job_status
        self.logger.info(job_status)
        return self.input


def check_harmony_job(config):
    """Function to check a harmony job id status and returns the status"""

    harmony_job = config.get("harmony_job")
    cmr_env = config.get("cmr_environment")

    harmony_client = utils.get_harmony_client(cmr_env)
    job_status = harmony_client.status(harmony_job)

    return job_status.get('status')


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
