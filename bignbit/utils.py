"""Module for functions used by more than one lambda"""
import hashlib
import os
import pathlib
import re
from datetime import datetime

import boto3
import harmony.config
import requests
from harmony import Environment, Client

ED_USER = ED_PASS = None
EDL_USER_TOKEN = {}
HARMONY_CLIENT = None


def get_edl_creds() -> (str, str):
    """
    Get EDL username and password from SSM.

    Returns
    -------
    (str, str)
        EDL username and EDL password
    """

    global ED_USER  # pylint: disable=W0603
    global ED_PASS  # pylint: disable=W0603

    ssm = boto3.client('ssm', region_name='us-west-2')

    if not ED_USER:
        edl_user_ssm_name = os.environ.get('EDL_USER_SSM')
        ssm_edl_user = ssm.get_parameter(
            Name=edl_user_ssm_name, WithDecryption=True
        )['Parameter']['Value']
        ED_USER = ssm_edl_user

    if not ED_PASS:
        edl_pass_ssm_name = os.environ.get('EDL_PASS_SSM')
        ssm_edl_pass = ssm.get_parameter(
            Name=edl_pass_ssm_name, WithDecryption=True
        )['Parameter']['Value']
        ED_PASS = ssm_edl_pass

    return ED_USER, ED_PASS


def get_cmr_user_token(edl_user: str, edl_pass: str, cmr_env: str) -> str:
    """
    Get a valid user token for the given user

    Parameters
    ----------
    edl_user
      EDL username
    edl_pass
      EDL password for user
    cmr_env
      CMR/URS environment to generate token in

    Returns
    -------
    str
      The token that can be used to query CMR
    """
    global EDL_USER_TOKEN  # pylint: disable=W0603
    if EDL_USER_TOKEN and datetime.now() < EDL_USER_TOKEN['expiration_date']:
        return EDL_USER_TOKEN['access_token']

    urs_get_tokens_url = f'https://{"uat." if cmr_env == "UAT" else ""}urs.earthdata.nasa.gov/api/users/tokens'
    urs_revoke_token_url = f'https://{"uat." if cmr_env == "UAT" else ""}urs.earthdata.nasa.gov/api/users/revoke_token'
    urs_create_token_url = f'https://{"uat." if cmr_env == "UAT" else ""}urs.earthdata.nasa.gov/api/users/token'

    with requests.Session() as session:
        session.auth = (edl_user, edl_pass)

        # Get existing user tokens
        get_tokens_request = session.request('get', urs_get_tokens_url)
        get_tokens_response = session.get(get_tokens_request.url, timeout=10)
        get_tokens_response.raise_for_status()
        tokens = get_tokens_response.json()

        # Filter expired tokens
        tokens = [{
            "access_token": t["access_token"],
            "expiration_date": datetime.strptime(t['expiration_date'], '%m/%d/%Y')
        } for t in tokens]
        valid_tokens = list(filter(lambda t: datetime.now() < t['expiration_date'], tokens))
        expired_tokens = list(filter(lambda t: datetime.now() >= t['expiration_date'], tokens))

        # If there are no valid tokens and two expired tokens, need to revoke one of the expired tokens
        if len(valid_tokens) == 0 and len(expired_tokens) == 2:
            revoke_token_request = session.request('post', urs_revoke_token_url,
                                                   params={'token': next(iter(expired_tokens))['access_token']},
                                                   timeout=10)
            revoke_token_response = session.post(revoke_token_request.url)
            revoke_token_response.raise_for_status()

        # If there are no valid tokens, need to create one
        if len(valid_tokens) == 0:
            create_token_request = session.request('post', urs_create_token_url, timeout=10)
            create_token_response = session.post(create_token_request.url)
            create_token_response.raise_for_status()
            new_token = create_token_response.json()
            new_token["expiration_date"] = datetime.strptime(new_token['expiration_date'], '%m/%d/%Y')
            valid_tokens.insert(0, new_token)

    EDL_USER_TOKEN = next(iter(valid_tokens))
    return EDL_USER_TOKEN['access_token']


def get_umm_json(granule_concept_id: str, cmr_environment):
    """
    Get the granuleUR for the given concept ID

    Parameters
    ----------
    granule_concept_id: str
      the concept ID for the granule to find

    cmr_environment: str
      CMR environment used to retrieve user token

    Returns
    -------
    dict
      The umm-json document
    """

    edl_user, edl_pass = get_edl_creds()
    token = get_cmr_user_token(edl_user, edl_pass, cmr_environment)

    cmr_link = f'https://cmr.{"uat." if cmr_environment == "UAT" else ""}earthdata.nasa.gov/search/concepts/{granule_concept_id}.umm_json'
    umm_json_response = requests.get(cmr_link, headers={'Authorization': f'Bearer {token}'}, timeout=10)
    umm_json_response.raise_for_status()
    umm_json = umm_json_response.json()

    return umm_json


def sha512sum(filepath: pathlib.Path):
    """
    Generate a SHA512 hash for the given file

    Parameters
    ----------
    filepath
      path to file
    Returns
    -------
      SHA512 hash of file contents
    """
    hash512 = hashlib.sha512()
    barray = bytearray(128 * 1024)
    mem_view = memoryview(barray)
    with open(filepath, 'rb', buffering=0) as file:
        for each in iter(lambda: file.readinto(mem_view), 0):
            hash512.update(mem_view[:each])
    return hash512.hexdigest()


def upload_cnm(bucket_name: str, key_name: str, cnm_content: str) -> str:
    """
    Upload CNM message into a s3 bucket

    Parameters
    ----------
    bucket_name: str
      Bucket name containing where CNM should be uploaded

    key_name: str
      Key to object location in bucket

    cnm_content: str
      The CNM message to upload

    Returns
    -------
    S3 URI of new object
    """
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Body=cnm_content,
        Bucket=bucket_name,
        Key=key_name
    )
    return f's3://{bucket_name}/{key_name}'


def upload_to_s3(filepath: pathlib.Path, bucket_name: str, object_key: str):
    """
    Uploads a file to S3

    Parameters
    ----------
    filepath
      path to file
    bucket_name
      destination bucket name
    object_key
      object key name in bucket

    Returns
    -------
    str
      s3 uri of new object
    """
    s3_client = boto3.client('s3')
    s3_client.upload_file(str(filepath), bucket_name, object_key)

    return f's3://{bucket_name}/{object_key}'


def checksum_and_upload(filepath: pathlib.Path, bucket_name: str, object_key: str) -> (str, str, str):
    """
    Create a checksum for the given file then upload it to s3

    Parameters
    ----------
    filepath: pathlib.Path
      path to file to upload
    bucket_name: str
      S3 bucket name
    object_key: str
      S3 object key

    Returns
    -------
    checksum_type: str
      The name of the checksum algorithm used
    checksum: str
      The checksum value
    s3_uri: str
      The full s3:// uri to the new object that was uploaded
    """
    checksum_type = "SHA512"
    checksum = sha512sum(filepath)

    s3_uri = upload_to_s3(filepath, bucket_name, object_key)

    return checksum_type, checksum, s3_uri


def get_harmony_client(environment_str: str) -> harmony.Client:
    """
    Return a harmony client configured for the given environment.

    Default to UAT if the string is invalid.

    Parameters
    ----------
    environment_str
        String representation of the desired environment

    Returns
    ----------
    harmony.Client
        Client configured for given environment
    """

    harmony_environ = Environment.UAT
    if environment_str.upper() in ("SIT", "SANDBOX", "SBX"):
        harmony_environ = Environment.UAT
    elif environment_str.upper() == "UAT":
        harmony_environ = Environment.UAT
    elif environment_str.upper() in ("OPS", "PROD"):
        harmony_environ = Environment.PROD

    global HARMONY_CLIENT  # pylint: disable=W0603
    if not HARMONY_CLIENT:
        HARMONY_CLIENT = Client(
        env=harmony_environ,
        auth=get_edl_creds(),
        should_validate_auth=False
    )

    return HARMONY_CLIENT


def extract_mgrs_grid_code(granule_umm_json: dict) -> str:
    """
    Try to retrieve the MGRS Grid Code for this granule.

    Parameters
    ----------
    granule_umm_json
      umm json for the granule
    Returns
    -------
    str
      the MGRS Grid Code

    Raises
    ------
    KeyError
      if no MGRS Grid Code could be found
    """
    if 'AdditionalAttributes' in granule_umm_json:
        tile_id = next(filter(lambda x: x['Name'] == 'MGRS_TILE_ID', granule_umm_json['AdditionalAttributes']), None)
        if tile_id:
            tile_id = tile_id['Values'][0]
            return tile_id

    granule_id = granule_umm_json['GranuleUR']
    if len(granule_id.split("_")) > 3:
        potential_mgrs_grid_code = granule_id.split("_")[3]
        if re.search("^T\\w{5}$", potential_mgrs_grid_code):  # pylint: disable=no-else-return
            return potential_mgrs_grid_code
        elif match := re.search("[_.](T\\w{5})[_.]", granule_id):
            return match.group(1)
    else:
        raise KeyError(f'MGRS_TILE_ID could not be extracted from GranuleUR for granule {granule_umm_json["GranuleUR"]}')

    raise KeyError(f'MGRS_TILE_ID was not found in AdditionalAttributes for granule {granule_umm_json["GranuleUR"]}')
