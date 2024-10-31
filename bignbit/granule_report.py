"""lambda function to generate a report for status of processed granules"""
import json
import logging
import os
import requests
import boto3
import botocore

from bignbit.utils import get_edl_creds, get_cmr_user_token

def lambda_handler(event, context):
    """
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
    logger = logging.getLogger('granule_report')
    levels = {
        'critical': logging.CRITICAL, 'error': logging.ERROR,
        'warn': logging.WARNING, 'warning': logging.WARNING,
        'info': logging.INFO, 'debug': logging.DEBUG
    }
    logger.setLevel(levels.get(os.environ.get('LOGGING_LEVEL', 'info')))

    logger.debug("Processing event %s", json.dumps(event))

    s3_client = boto3.client('s3')

    collection_shortname = event["collection_shortname"]
    cmr_query_start_time = event["start_time"]
    cmr_query_end_time = event["end_time"]

    cmr_env = os.environ['CMR_ENVIRONMENT']
    pobit_audit_bucket_name = os.environ['POBIT_AUDIT_BUCKET_NAME']

    granules = query_for_granules(collection_shortname, cmr_query_start_time, cmr_env)
    for granule in granules:
        granuleUR = granule[0]
        granule_concept = granule[1]

        browse_image_executions = get_browse_executions(granuleUR)
        cma_messages = get_cma_paths(granuleUR)
        cnm_paths = get_cnm_paths(granule)

        for cnm in cnm_paths:
            cnm_path = cnm[0]
            cnm_identifier = cnm[1]

            cnm_r_path = cnm_path[:-5] + "-r.json"

            try:
                s3_client.head_object(Bucket=pobit_audit_bucket_name, Key='file_path')
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    # The key does not exist.
                    ...
                elif e.response['Error']['Code'] == 403:
                    # Unauthorized, including invalid bucket
                    ...
                else:
                    # Something else has gone wrong.
                raise 

            report_row = 


def query_for_granules(collection_shortname, start_time, end_time, cmr_env):
    """
    Queries CMR for the granules belonging to the specified collection
    
    Parameters
    ----------
    collection_shortname : str
        the shortname of the collection
    start_time :  str
        the start time to query within
    end_time : str
        the end time to query within
    cmr_env : str
        the environment to query (UAT, PROD)

    Returns
    -------
    granule_list : list 
        list of tuples containing (granuleUR, concept_id)
    """

    granule_list = []

    edl_user, edl_pass = get_edl_creds()
    token = get_cmr_user_token(edl_user, edl_pass, cmr_env)

    headers = {'Authorization': f'Bearer {token}'}
    params={
          'short_name': collection_shortname,
          'temporal': str(start_time) + ',' + str(end_time),
          'page_size': 100
          }
    
    cmr_link = f'https://cmr.{"uat." if cmr_env == "UAT" else ""}earthdata.nasa.gov/search/granules.umm_json'
    response = requests.get(cmr_link, headers=headers, params=params, timeout=10)

    data = [(item['umm']['GranuleUR'], item['meta']['concept-id']) for item in response.json()]
    granule_list.append(data)

    while 'CMR-Search-After' in response.headers:
        headers = {
            'Authorization': f'Bearer {token}',
            'CMR-Search-After': response.headers.get('CMR-Search-After')
            }
        response = requests.get(cmr_link, headers=headers, params=params, timeout=10)
        
        data = [(item['umm']['GranuleUR'], item['meta']['concept-id']) for item in response.json()]
        granule_list.append(data)

    return granule_list


def get_browse_executions(granule):
    """
    Get the browse image workflow execution IDs for a granule
    
    Parameters
    ----------
    granule : str
        The granule to search
        
    Returns
    -------
    id : str
        the execution ID, 'Missing' if none
    """
    pass


def get_cma_message(granule):
    """
    """
    pass

def get_