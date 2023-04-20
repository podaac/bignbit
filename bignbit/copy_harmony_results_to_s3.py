# pylint: disable=protected-access
"""Cumulus lambda class to create copy harmony job results into s3"""

import logging
import os
import botocore
from cumulus_logger import CumulusLogger
from cumulus_process import Process, s3

from bignbit import utils

CUMULUS_LOGGER = CumulusLogger('copy_harmony_results_to_s3')


class CMA(Process):
    """Cumulus class to copy harmony results to s3"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self):
        """
        Copys the resulting files of a harmony call to s3

        Returns
        ----------
        CMA message
        """
        files = self.input.get('granules')[0].get('files')
        data_file = None
        for file in files:
            if file.get('type') == 'data':
                data_file = file

        uploaded_files = copy_harmony_to_s3(self.config, self.path, data_file)
        self.input['big'] = uploaded_files
        return self.input


def copy_harmony_to_s3(config, path, data_file):
    """Function to copy harmony resutls into s3 and retunr list of dict with info on new file"""

    harmony_job = config.get('harmony_job')
    cmr_env = config.get('cmr_environment')
    harmony_client = utils.get_harmony_client(cmr_env)
    urls = harmony_client.result_urls(harmony_job)
    current_item = config.get('current_item')
    variable = current_item.get('id')
    prefix = os.path.dirname(data_file['key'])
    bucket = data_file.get('bucket')

    uploaded_files = []

    for url in urls:

        local_file = harmony_client._download_file(url, directory=path, overwrite=True)
        output_file_basename = os.path.basename(local_file)

        upload_file_dict = {
            "fileName": output_file_basename,
            "bucket": bucket,
            "key": f'{prefix}/{output_file_basename}',
            "size": os.path.getsize(local_file),
            "checksumType": "SHA512",
            "checksum": utils.sha512sum(local_file),
            "variable": variable
        }

        s3_link = f's3://{upload_file_dict["bucket"]}/{upload_file_dict["key"]}'
        upload_file_to_s3(local_file, s3_link)
        uploaded_files.append(upload_file_dict)

    return uploaded_files


def upload_file_to_s3(filename, uri):
    """ Upload a local file to s3 if collection payload provided

    Parameters
    ----------
    filename: str
        path location of the file
    uri: str
        s3 string of file location
    Returns
    ----------
    None
    """
    try:
        return s3.upload(filename, uri, extra={})
    except botocore.exceptions.ClientError as ex:
        base_file = os.path.basename(os.path.basename(filename))
        CUMULUS_LOGGER.error(
            f"Error uploading file {base_file}: {ex}",
            exc_info=True
        )
        raise ex


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

    cumulus_results = CMA.cumulus_handler(event, context=context)
    return cumulus_results.get('payload').get('big')


if __name__ == "__main__":
    CMA()
