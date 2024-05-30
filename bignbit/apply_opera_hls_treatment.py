# pylint: disable=invalid-name
"""
Transforms each image in the input using specific processing required to produce an image for display in GITC
"""
import logging
import os
import pathlib
import pickle
from typing import Dict, List

import boto3
import importlib_resources
from cumulus_logger import CumulusLogger
from cumulus_process import Process
from osgeo import gdal

from bignbit import utils

CUMULUS_LOGGER = CumulusLogger('apply_opera_hls_treatment')


def load_mgrs_gibs_intersection():
    """
        load gibs intersection json pickle file
    """
    ref = importlib_resources.files('bignbit').joinpath('data/mgrs_gibs_intersection.json.pickle')
    with ref.open('rb') as fp:
        data = pickle.load(fp)
    return data


MGRS_GIBS_INTERSECTION = load_mgrs_gibs_intersection()


class CMA(Process):
    """
    A cumulus message adapter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self) -> List[Dict]:
        """
        Applies transformations to the image file in order to make it suitable for display by GITC

        Returns
        -------
        List[Dict]
          A list of CMA file dictionaries pointing to the transformed image(s)
        """
        cma_file_list = self.input['big']

        mgrs_grid_code = utils.extract_mgrs_grid_code(self.input['granule_umm_json'])
        file_metadata_list = transform_images(cma_file_list, pathlib.Path(f"{self.path}"), mgrs_grid_code)
        del self.input['big']
        self.input['big'] = file_metadata_list
        return self.input


def transform_images(cma_file_list: List[Dict], temp_dir: pathlib.Path, mgrs_grid_code: str) -> List[Dict]:
    """
    Applies special OPERA HLS processing to each input image. Each input image will result in multiple output transformed
    images.

    Parameters
    ----------
    cma_file_list
        List of CMA file metadata dicts for images to transform
    temp_dir
        Temporary working directory on local disk
    mgrs_grid_code
        MGRS grid code for the current granule being processed

    Returns
    -------
    List[Dict]
        List of CMA File metadata dicts for each transformed image
    """
    file_metadata_results = []
    for cma_file_meta in cma_file_list:
        granule_filename = cma_file_meta['filename'] if 'filename' in cma_file_meta else cma_file_meta['fileName']
        CUMULUS_LOGGER.info(f'Processing file {granule_filename}')

        # Download the file for processing
        source_image_local_filepath = get_file(cma_file_meta['bucket'], cma_file_meta['key'],
                                               temp_dir.joinpath(cma_file_meta['key']))
        CUMULUS_LOGGER.info(f'Downloaded: {source_image_local_filepath}')

        # Reproject and resample image to sub-tiles
        transformed_images_dirpath = temp_dir.joinpath(source_image_local_filepath.stem)
        transformed_images_dirpath.mkdir(parents=True)
        transformed_images_filepaths = the_opera_hls_treatment(source_image_local_filepath, transformed_images_dirpath,
                                                               mgrs_grid_code)
        CUMULUS_LOGGER.info(f'Created new images: {[str(t) for t in transformed_images_filepaths]}')

        # Create new file metadata for each new image
        file_metadata_dicts = create_file_metadata(cma_file_meta, transformed_images_filepaths)
        file_metadata_results.extend(file_metadata_dicts)

        # Upload new images to s3
        s3_uris = upload_transformed_images(file_metadata_dicts)
        CUMULUS_LOGGER.info(f'Uploaded files: {s3_uris}')

        CUMULUS_LOGGER.info(f'Finished processing file {granule_filename}')

    # List returned is CMA file metadata dicts for all images.
    return file_metadata_results


def get_file(bucket: str, key: str, local_filepath: pathlib.Path) -> pathlib.Path:
    """
    Download a file from s3

    Parameters
    ----------
    bucket
        Name of bucket
    key
        Key of object in bucket
    local_filepath
        Full path including filename of location object should be downloaded to

    Returns
    -------
    pathlib.Path
        Path to downloaded file
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    obj = bucket.Object(key)

    local_filepath.resolve().parent.mkdir(parents=True, exist_ok=True)
    with open(local_filepath, 'wb') as data:
        obj.download_fileobj(data)

    return local_filepath


def the_opera_hls_treatment(source_image_filepath: pathlib.Path, working_dirpath: pathlib.Path,
                            mgrs_grid_code: str) -> List[pathlib.Path]:
    """
    What is the OPERA treatment? Well, it is special.

    GITC currently requires the images to meet 2 conditions
     1. Must be in EPSG:4326 projection
     2. Each image must be at 31.25 meter resolution

    Eventually, condition #2 might be relaxed but for now it is a strict requirement and is the reason for the
    2.74658203125e-4 "magic number" https://en.wikipedia.org/wiki/Magic_number_(programming) in the implementation
    below. However, simply rescaling to this resolution is insufficient because that does not match up with the
    MGRS/GITC tiles used to display the images on a globe. Therefore, it is also required to subdivide each source
    image into multiple "sub_tile"s that match the bounds that GITC needs in order to geolocate them correctly. By
    rescaling and bounding by these sub_tiles, the resulting tifs are then processable by GITC

    IMPACT did similar processing with the HLS code and that code can be found here:
    https://github.com/NASA-IMPACT/hls-browse_imagery/blob/c13b9abe7d9625ee4e375a8406ff32ada0a89658/hls_browse_imagery_creator/granule_to_gibs.py

    Parameters
    ----------
    source_image_filepath
        Original browse image tif as delivered by the project
    working_dirpath
        Directory used for intermediate files
    mgrs_grid_code
        MGRS grid code for the current granule being processed

    Returns
    -------
    List[pathlib.Path]
        Absolute paths to each transformed output tif file
    """
    try:
        # Need to strip off the leading 'T' from the actual grid code in order to look it up in the json data
        # this is done using a slice on the string mgrs_grid_code[1:]
        if mgrs_grid_code.startswith('T'):
            sub_tiles = MGRS_GIBS_INTERSECTION[mgrs_grid_code[1:]]
        else:
            sub_tiles = MGRS_GIBS_INTERSECTION[mgrs_grid_code]
    except KeyError as e:
        raise KeyError(f"Could not locate grid code {mgrs_grid_code[1:]} in mgrs_gibs_intersection.json.pickle") from e

    result_image_filepaths = []
    for sub_tile in sub_tiles:
        # Build a new filename for each sub tile by locating the MGRS tile id in the source filename and
        # appending f"_{sub_tile['GID'}}" immediately after the MGRS tile id.
        # Example:
        #  OPERA_L3_DSWx-HLS_T01WCU_20210827T002611Z_20230131T090316Z_S2A_30_v1.0_BROWSE        (original)
        #  OPERA_L3_DSWx-HLS_T01WCU_318143_20210827T002611Z_20230131T090316Z_S2A_30_v1.0_BROWSE (new)
        # Each sub tile is also placed in its own sub-directory by GID
        destination_subtile_dirpath = working_dirpath.joinpath(sub_tile['GID'])
        destination_subtile_dirpath.mkdir(parents=True)
        sub_tile_filename = f"{mgrs_grid_code}_{sub_tile['GID']}".join(
            source_image_filepath.stem.split(mgrs_grid_code)) + source_image_filepath.suffix
        destination_subtile_filepath = destination_subtile_dirpath.joinpath(sub_tile_filename)
        result_image_filepaths.append(destination_subtile_filepath)

        # Use gdalwarp to reproject and rescale each sub_tile
        gdal.Warp(str(destination_subtile_filepath), str(source_image_filepath),
                  outputBounds=(sub_tile['minlon'], sub_tile['minlat'], sub_tile['maxlon'], sub_tile['maxlat']),
                  dstSRS="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs", xRes=2.74658203125e-4,
                  yRes=2.74658203125e-4, creationOptions=["COMPRESS=LZW", "TILED=YES"], format="GTiff")

    return result_image_filepaths


def create_file_metadata(original_cma_file_meta: dict, transformed_images_filepaths: List[pathlib.Path]) -> List[Dict]:
    """
    Generate a new CMA file metadata dictionary for each transformed image using the original CMA metadata as a
    template.

    One additional key is added to the dict 'local_filepath' which is the full absolute filepath to the transformed
    image on disk to facilitate uploads in a later step.

    Parameters
    ----------
    original_cma_file_meta
        CMA file metadata dict of the original source image
    transformed_images_filepaths
        Local filepaths to each output transformed image

    Returns
    -------
    List[Dict]
        List of CMA file metadata dict for each output transformed image
    """
    new_cma_file_meta_list = []
    for transformed_image in transformed_images_filepaths:
        new_cma_file_meta = original_cma_file_meta.copy()
        new_cma_file_meta["fileName"] = transformed_image.name
        # Takes the 'key' from the original and replace just the last part with the new filename
        new_cma_file_meta["key"] = str(pathlib.Path(*pathlib.Path(original_cma_file_meta["key"]).parts[0:-1]).joinpath(
            transformed_image.name))
        new_cma_file_meta["local_filepath"] = str(transformed_image.resolve())

        new_cma_file_meta_list.append(new_cma_file_meta)

    return new_cma_file_meta_list


def upload_transformed_images(image_file_metadatas: List[Dict]) -> List[str]:
    """
    Uploads to s3

    Parameters
    ----------
    image_file_metadatas
      List of CMA file dict for files being uploaded

    Returns
    -------
    str
      s3 uri to uploaded object
    """
    s3_uris = []
    for image_file_metadata in image_file_metadatas:
        s3_uris.append(utils.upload_to_s3(image_file_metadata['local_filepath'], image_file_metadata['bucket'],
                                          image_file_metadata['key']))
    return s3_uris


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
