"""
Finds an image file in the list of files for a granule based on a regex
"""
import logging
import os
import re
from typing import Dict, List

from cumulus_logger import CumulusLogger
from cumulus_process import Process

CUMULUS_LOGGER = CumulusLogger('identify_image_file')


class NoMatchingFile(Exception):
    """
    Exception thrown if BIG does not find a file that matches the configured regex
    """


class CMA(Process):
    """
    A cumulus message adapter
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self) -> List[Dict]:
        """
        Locates an image file based on a regex specified in the configuration for this dataset

        Returns
        -------
        List[Dict]
          A list of CMA file dictionaries extracted from granules.files that match the given regex

        """
        image_filename_regex = self.input['datasetConfigurationForBIG']['config']['imageFilenameRegex']
        granule_file_list = self.input['granules'][0]['files']

        self.input['big'] = [find_image_by_regex(image_filename_regex, granule_file_list)]
        return self.input


def find_image_by_regex(regex: str, files: List[Dict]) -> Dict:
    """
    Searches through the given file list for the first file that matches the given regex

    Parameters
    ----------
    regex: str
      The regex used to match

    files: List[Dict]
      The list of files to search through

    Returns
    -------
    dict
      The first matching file
    """
    pattern = re.compile(regex)

    for granule_file in files:
        granule_filename = granule_file['filename'] if 'filename' in granule_file else granule_file['fileName']
        if pattern.search(granule_filename):
            return granule_file

    raise NoMatchingFile(f"{regex} does not match any file name from the given files")


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
