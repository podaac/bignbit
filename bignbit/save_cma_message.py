"""lambda function that stores the CMA message into a s3 bucket"""
import json
import logging

import boto3


def upload_cma(pobit_audit_bucket: str, cma_key_name: str, cma_content: dict):
    """
    Upload CMA message into a s3 bucket

    Parameters
    ----------
    pobit_audit_bucket: str
      Bucket name containing where CMA should be uploaded

    cma_key_name: str
      Key to object location in bucket

    cma_content: dict
      The CMA message to upload

    Returns
    -------
    None
    """
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Body=json.dumps(cma_content, default=str).encode("utf-8"),
        Bucket=pobit_audit_bucket,
        Key=cma_key_name
    )


def lambda_handler(event, _context):
    """handler that gets called by aws lambda
    Parameters
    ----------
    event: dictionary
        event from a lambda call
    context: dictionary
        context from a lambda call

    """
    logger = logging.getLogger('save_cma_message')

    pobit_audit_bucket = event['pobit_audit_bucket']
    cma_key_name = event['cma_key_name']
    cma_content = event['cma_content']

    gitc_id = cma_content['identifier']

    logger.info("Uploading CMA message to S3 for uuid %s", gitc_id)
    upload_cma(pobit_audit_bucket, cma_key_name, cma_content)
