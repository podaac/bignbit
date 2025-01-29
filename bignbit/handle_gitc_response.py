"""lambda function used to be triggered when receiving data from GITC"""
import json
import logging
import os
from json import loads

from bignbit import utils


def handler(event, _):
    """
    Handler of the function

    Parameters
    ----------
    event: dictionary

    Returns
    ----------
    Status: dictionary

    """
    logger = logging.getLogger('handle_gitc_response')
    levels = {
        'critical': logging.CRITICAL, 'error': logging.ERROR,
        'warn': logging.WARNING, 'warning': logging.WARNING,
        'info': logging.INFO, 'debug': logging.DEBUG
    }
    logger.setLevel(levels.get(os.environ.get('LOGGING_LEVEL', 'info')))

    logger.debug("Processing event %s", json.dumps(event))

    for message in event["Records"]:
        message_body = loads(message["body"])
        gitc_id = message_body["identifier"]
        collection_name = message_body["collection"]
        cmr_env = os.environ['CMR_ENVIRONMENT']

        granule_concept_id = gitc_id.rpartition('_')[-1]
        umm_json = utils.get_umm_json(granule_concept_id, cmr_env)
        granule_ur = umm_json['GranuleUR']

        cnm_key_name = os.environ['POBIT_AUDIT_PATH_NAME'] + "/" + collection_name + "/" + granule_ur + "." + message_body['submissionTime'] + "." + "cnm-r.json"

        s3_path = utils.upload_cnm(os.environ['POBIT_AUDIT_BUCKET_NAME'], cnm_key_name, json.dumps(message_body))

        logging.info('CNM-R uploaded to %s for id %s',s3_path, gitc_id)

    return {"statusCode": 200, "body": "All good"}
