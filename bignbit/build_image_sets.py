"""lambda function that translates the output of BIG into ImageSets that can be sent to GITC"""

import logging
import os

from cumulus_logger import CumulusLogger
from cumulus_process import Process

from bignbit.image_set import from_big_output, IncompleteImageSet

CUMULUS_LOGGER = CumulusLogger('build_image_sets')


class ImageSetGenerator(Process):
    """
    Class for constructing ImageSet's based on the output provided from the BIG task

    Attributes
    ----------
    logger: logger
        cumulus logger
    config: dictionary
        configuration from cumulus
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self):
        """
        Main process to send daily Browse Image data to GIBS

        Returns
        ----------
        dict
            Payload that is returned to the cma which is a dictionary with \
            list of granules
        """

        response_payload = {}

        if self.input is not None:
            try:
                image_sets = from_big_output(self.input['big'])
                self.logger.info(f"Found {len(image_sets)} image sets to process {[ims.name for ims in image_sets]}")
            except IncompleteImageSet as ex:
                self.logger.error("Missing files. Unable to send to GIBS", exc_info=True)
                raise Exception("Missing files. Unable to send to GIBS") from ex  # pylint: disable=broad-exception-raised

            response_payload = self.input.copy()
            del response_payload['big']
            response_payload['pobit'] = []

            for image_set in image_sets:
                image_set.name = image_set.name + '_' + self.input['granules']['cmrConceptId']
                
                response_payload['pobit'].append({
                    'image_set': image_set._asdict(),
                    'cmr_provider': self.config.get('cmr_provider'),
                    'collection_name': self.config.get('collection').get('name'),
                })

        return response_payload


def lambda_handler(event, context):
    """
    handler that gets called by aws lambda
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
    # pylint: disable=duplicate-code
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

    return ImageSetGenerator.cumulus_handler(event, context=context)


if __name__ == "__main__":
    ImageSetGenerator()
