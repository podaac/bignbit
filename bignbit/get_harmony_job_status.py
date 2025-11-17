"""Cumulus lambda class to check harmony job status"""
import json
import logging
import os

from cumulus_logger import CumulusLogger
from cumulus_process import Process

from bignbit import utils
from bignbit.utils import json_dumps_with_datetime

CUMULUS_LOGGER = CumulusLogger('get_harmony_job_status')


class HarmonyJobIncompleteError(Exception):
    """Exception raised when a harmony job is not complete"""

    def __init__(self, message):
        super().__init__(message)


class HarmonyJobFailedError(Exception):
    """Exception raised when a harmony job has failed"""

    def __init__(self, message):
        super().__init__(message)


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

        harmony_job_id = self.config.get("harmony_job")
        cmr_environment = self.config.get("cmr_environment")

        job_status = check_harmony_job(harmony_job_id, cmr_environment)
        self.input['harmony_job_status'] = job_status
        self.logger.info(job_status)
        return self.input


def check_harmony_job(harmony_job_id: str, cmr_env: str = None) -> str:
    """
    Function to check a harmony job id status and returns the status

    Parameters
    ----------
    harmony_job_id: str
        The harmony job id to check
    cmr_env: str
        The CMR environment to use, defaults to None which uses the default environment
    Returns
    ----------
    str
        The status of the harmony job if 'successful' or
        raises an exception if the job has failed or is incomplete.
    """

    harmony_client = utils.get_harmony_client(cmr_env)
    job_status = harmony_client.status(harmony_job_id)

    # For a successful job, return the status; for all other states, raise an exception.
    if job_status.get('status') == 'successful':
        return job_status.get('status')

    # If the job is still running or accepted, raise an exception that will be retried by the step function workflow.
    if job_status.get('status') in ['accepted', 'running']:
        raise HarmonyJobIncompleteError(
            f'Harmony job {harmony_job_id} is not complete. Status: {json_dumps_with_datetime(job_status)}')

    # If the job has failed, raise an exception that will cause the step function workflow to fail.
    raise HarmonyJobFailedError(
        f'Harmony job {harmony_job_id} has failed. Status: {json_dumps_with_datetime(job_status)}')


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
