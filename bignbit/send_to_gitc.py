"""lambda function used to send CNM to GIBS"""

import json
import logging
import os
from datetime import datetime, timezone

import boto3
from cumulus_logger import CumulusLogger
from cumulus_process import Process

from bignbit.image_set import ImageSet, to_cnm_product_dict

CUMULUS_LOGGER = CumulusLogger('send_to_gitc')

GIBS_REGION_ENV_NAME = "GIBS_REGION"
GIBS_SQS_URL_ENV_NAME = "GIBS_SQS_URL"


class NotifyGitc(Process):
    """
    Class for notifying GITC (via SQS) that a Browse Image is ready to transfer

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

        notification_id = ""

        if self.input is not None:
            # Send ImageSet(s) to GITC for processing
            collection_name = self.input.get('collection_name')
            cmr_provider = self.input.get('cmr_provider')
            image_set = ImageSet(**self.input['image_set'])
            gitc_id = image_set.name

            notification_id = notify_gitc(image_set, cmr_provider, gitc_id, collection_name)

        return notification_id


def notify_gitc(image_set: ImageSet, cmr_provider: str, gitc_id: str, collection_name: str):
    """
    Builds and sends a CNM message to GITC

    Parameters
    ----------
    image_set: ImageSet
      The image set to send
    cmr_provider: str
      The provider sent in the CNM message
    gitc_id: str
      The unique identifier for this particular request to GITC
    collection_name: str
      Collection that this image set belongs to

    Returns
    -------
    cnm_id: str
      The identifier of this CNM
    """

    queue_url = os.environ.get(GIBS_SQS_URL_ENV_NAME)
    CUMULUS_LOGGER.info(f'Sending SQS message to GITC for image {image_set.name}')

    cnm = construct_cnm(image_set, cmr_provider, gitc_id, collection_name)

    cnm_json = json.dumps(cnm)
    sqs_message_params = {
        "QueueUrl": queue_url,
        "MessageBody": cnm_json,
        "MessageGroupId": cnm['collection']
    }
    CUMULUS_LOGGER.debug(f'CNM message for GIBS: {sqs_message_params}')

    gibs_region = os.environ.get(GIBS_REGION_ENV_NAME)

    sqs = boto3.client('sqs', region_name=gibs_region)

    response = sqs.send_message(**sqs_message_params)

    CUMULUS_LOGGER.debug(f'SQS send_message output: {response}')

    return cnm['identifier']


def construct_cnm(image_set: ImageSet, cmr_provider: str, gitc_id: str, collection_name: str):
    """
    Construct the CNM message for GITC

    Parameters
    ----------
    image_set: ImageSet
        ImageSet for one image to be sent to gibs
    cmr_provider: str
      The provider sent in the CNM message
    gitc_id: str
      The unique identifier for this particular request to GITC
    collection_name: str
      Collection that this image set belongs to

    Returns
    ----------
    cnm: dict
        CNM message
    """
    product = to_cnm_product_dict(image_set)
    submission_time = datetime.now(timezone.utc).isoformat()[:-9] + 'Z'
    CUMULUS_LOGGER.debug(image_set.image['variable'])
    new_collection = collection_name + "_" + image_set.image['variable']
    return {
        "version": "1.5.1",
        "duplicationid": image_set.name,
        "collection": new_collection,
        "submissionTime": submission_time,
        "identifier": gitc_id,
        "product": product,
        'provider': cmr_provider
    }


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

    return NotifyGitc.cumulus_handler(event, context=context)


if __name__ == "__main__":
    NotifyGitc()
