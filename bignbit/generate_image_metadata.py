"""
Creates and uploads to s3 an ImageMetadata-v1.2 xml file for each image in the input
"""
import logging
import os
import pathlib
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List

from cumulus_logger import CumulusLogger
from cumulus_process import Process

from bignbit import utils

CUMULUS_LOGGER = CumulusLogger('generate_image_metadata')

# Subtypes are defined in the GIBS ICD
# https://wiki.earthdata.nasa.gov/download/attachments/176426242/423-ICD-009_RevB_GIBS%20Imagery%20Provider%20ICD%20%28Final%29.pdf?version=1&modificationDate=1645129702239&api=v2
# Table 5.2-4
BROWSE_IMAGE_EXTENSION_SUBTYPES = {
    '.tif': 'geotiff',
    '.tiff': 'geotiff',
    '.png': 'png',
    '.jpg': 'jpeg',
    '.jpeg': 'jpeg',
    '.json': 'geojson',
    '.shp': 'shapefile'
}


class CMA(Process):
    """
    A cumulus message adapter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = CUMULUS_LOGGER

    def process(self) -> List[Dict]:
        """
        Constructs and uploads an ImageMetadata-v1.2 xml file for each image in the input
        Returns
        -------
        List[Dict]
          A list of CNM-ready file dicts for all image, wld, and ImageMetadata-v1.2 xml files
        """
        cma_file_list = self.input['big']
        # Flatten input list if needed
        if cma_file_list and any(isinstance(el, list) for el in cma_file_list):
            cma_file_list = [item for sublist in cma_file_list for item in sublist]
        granule_umm_json = self.input['granule_umm_json']

        file_metadata_list = generate_metadata(cma_file_list, granule_umm_json, pathlib.Path(f"{self.path}"))
        del self.input['granule_umm_json']
        del self.input['big']
        self.input['big'] = file_metadata_list
        return self.input


def generate_metadata(cma_file_list: List[Dict], granule_umm_json: dict, temp_dir: pathlib.Path) -> List[Dict]:
    """
    For each file in the list, create an ImageMetadata-v1.2 xml file and upload it to s3 in the same
    bucket and path as the image file.

    Also transforms each CMA file dict to a CNM-ready file dict.

    Parameters
    ----------
    cma_file_list
      List of files to process
    granule_umm_json
      umm-json document for the granule being processed
    temp_dir
      Temporary location to write xml file to prior to upload to s3

    Returns
    -------
    List[Dict]
      A list of CNM-ready file dicts for all image, wld, and ImageMetadata-v1.2 xml files
    """
    file_metadata_results = []
    for cma_file_meta in cma_file_list:
        granule_filename = cma_file_meta['filename'] if 'filename' in cma_file_meta else cma_file_meta['fileName']
        CUMULUS_LOGGER.info(f'Processing file {granule_filename}')

        # Get date information from umm-g
        begin, mid, end, dataday = extract_granule_dates(granule_umm_json)

        # Determine type and subtype for CNM
        granule_extension = pathlib.Path(granule_filename).suffix
        granule_type = "browse" if granule_extension in BROWSE_IMAGE_EXTENSION_SUBTYPES else "metadata"
        if granule_type == "browse":
            granule_subtype = BROWSE_IMAGE_EXTENSION_SUBTYPES.get(granule_extension, None)
        elif granule_extension.lower() == '.wld':
            granule_subtype = "world file"
        else:
            granule_subtype = None

        # Get partial id if it exists in umm-g
        try:
            partial_id = utils.extract_mgrs_grid_code(granule_umm_json)
        except KeyError:
            # No partial id for this granule
            partial_id = None
            CUMULUS_LOGGER.warn(f"No partial id found in metadata for {granule_filename}. Leaving partial id blank.")

        # Convert from CMA file dict to CNM file dict
        cnm_file_meta = transform_files_to_cnm_product_files(cma_file_meta, granule_type, granule_subtype, dataday)
        file_metadata_results.append(cnm_file_meta)

        # If this is a browse image, generate image metadata for it and upload it to s3
        if granule_type == 'browse':
            image_metadata_xml = create_metadata_xml(begin, mid, end, dataday, partial_id)
            temp_xml_path = write_image_metadata_xml(image_metadata_xml, temp_dir)
            image_metadata_xml_metadata = get_file_metadata_for_image_metadta_xml(temp_xml_path, cnm_file_meta)
            s3_uri = upload_image_metadata_xml(image_metadata_xml_metadata, temp_xml_path)
            CUMULUS_LOGGER.info(f'Uploaded file {s3_uri}')
            file_metadata_results.append(image_metadata_xml_metadata)

        CUMULUS_LOGGER.info(f'Finished processing file {granule_filename}')

    # List returned is CNM-ready file dicts for all image, wld, and xml files.
    return file_metadata_results


def write_image_metadata_xml(image_metadata_xml: ET.ElementTree, temp_dir: pathlib.Path) -> pathlib.Path:
    """
    Write the xml to a file

    Parameters
    ----------
    image_metadata_xml
      XML data to write
    temp_dir
      Temporary directory to write file to

    Returns
    -------
    pathlib.Path
      Path to location where file was written
    """
    temp_path = temp_dir.joinpath(f"{uuid.uuid4()}.xml")
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_path, 'wb') as file:
        image_metadata_xml.write(file, encoding='utf-8')

    return temp_path


def get_file_metadata_for_image_metadta_xml(image_metadata_xml_temp_filepath: pathlib.Path,
                                            cnm_file_meta: dict) -> dict:
    """
    Construct a CNM-compatible file dict for an image metadata xml file

    Parameters
    ----------
    image_metadata_xml_temp_filepath
      path to xml file
    cnm_file_meta
      file metadata of the image file that the image metadata xml is describing

    Returns
    -------
    dict
      CNM-compatible file dict for an image metadata xml file
    """
    image_metadata_file_metadata = cnm_file_meta.copy()

    image_metadata_xml_key = pathlib.Path(cnm_file_meta['key']).with_suffix('.xml')

    image_metadata_file_metadata["fileName"] = image_metadata_xml_key.name
    image_metadata_file_metadata["key"] = str(image_metadata_xml_key)
    image_metadata_file_metadata["type"] = "metadata"
    image_metadata_file_metadata["subtype"] = "ImageMetadata-v1.2"
    image_metadata_file_metadata["checksumType"] = "SHA512"
    image_metadata_file_metadata["checksum"] = utils.sha512sum(image_metadata_xml_temp_filepath)
    image_metadata_file_metadata["size"] = image_metadata_xml_temp_filepath.stat().st_size

    return image_metadata_file_metadata


def upload_image_metadata_xml(image_metadata_file_metadata: dict, temp_dir: pathlib.Path) -> str:
    """
    Uploads to s3

    Parameters
    ----------
    image_metadata_file_metadata
      CNM file dict for file being uploaded
    temp_dir
      temp path to file being uploaded

    Returns
    -------
    str
      s3 uri to uploaded object
    """
    return utils.upload_to_s3(temp_dir, image_metadata_file_metadata['bucket'], image_metadata_file_metadata['key'])


def transform_files_to_cnm_product_files(cma_file_meta: Dict, file_type: str, subtype: str, dataday: str) -> Dict:
    """
    Creates a CNM compatible file dict from a CMA file dict

    Parameters
    ----------
    cma_file_meta
      The CMA file metadata dict to convert
    file_type
      The CNM type to use for this file
    subtype
      The CNM subtype to use for this file
    dataday
      The dataday for this file

    Returns
    -------
    dict
      a CNM compatible file dict
    """
    cnm_file_meta = cma_file_meta.copy()
    if "filepath" in cnm_file_meta:
        cnm_file_meta["key"] = cnm_file_meta["filepath"]
        del cnm_file_meta["filepath"]
    if "name" in cnm_file_meta:
        cnm_file_meta["fileName"] = cnm_file_meta["name"]
        del cnm_file_meta["name"]
    if "path" in cnm_file_meta:
        del cnm_file_meta["path"]
    if "url_path" in cnm_file_meta:
        del cnm_file_meta["url_path"]
    if "filename" in cnm_file_meta:
        del cnm_file_meta["filename"]

    cnm_file_meta["type"] = file_type
    if subtype:
        cnm_file_meta["subtype"] = subtype

    # Technically variable and dataday are not CNM file attributes but BIG/pobit need them for processing
    if "variable" not in cnm_file_meta:
        cnm_file_meta["variable"] = "none"
    cnm_file_meta["dataday"] = dataday

    return cnm_file_meta


def extract_granule_dates(granule_umm_json: dict) -> (str, str, str, str):
    """
    Parse the begin, midpoint, end, and dataday for this granule

    Parameters
    ----------
    granule_umm_json
      umm json for this granule
    Returns
    -------
    begin
      range beginning date time as string formatted "%Y-%m-%dT%H:%M:%S.%fZ"
    mid
      date time halfway between begin and end as string formatted "%Y-%m-%dT%H:%M:%S.%fZ"
    begin
      range ending date time as string formatted "%Y-%m-%dT%H:%M:%S.%fZ"
    dataday
      day this granule applies to as string formatted "%Y%j
    """
    time_range_dict = granule_umm_json['TemporalExtent']['RangeDateTime']

    beginning_time_dt = parse_datetime(time_range_dict["BeginningDateTime"])
    ending_time_dt = parse_datetime(time_range_dict["EndingDateTime"])
    middle_time_dt = beginning_time_dt + (ending_time_dt - beginning_time_dt) / 2

    begin = beginning_time_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    mid = middle_time_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end = ending_time_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    middle_year = middle_time_dt.strftime("%Y")
    day_of_year = middle_time_dt.strftime('%j')
    dataday = middle_year + day_of_year

    return begin, mid, end, dataday


def parse_datetime(datetime_str: str) -> datetime:
    """
    Parses a datetime string into a datetime object.

    Parameters
    ----------
    datetime_str
      Datetime in str format to parse

    Returns
    -------
    datetime
      a datetime object
    """
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")


def create_metadata_xml(beginning_time: str, middle_time: str, ending_time: str, dataday: str,
                        partial_id: str = None) -> ET.ElementTree:
    """
    Create an ImageMetadata-v1.2 XML Element tree

    Parameters
    ----------
    beginning_time
      formatted datetime string for data begin date time
    middle_time
      formatted datetime string for data midpoint date time
    ending_time
      formatted datetime string for data end date time
    dataday
      string if format %Y%j for day of year the data represents
    partial_id
      partial id associated with data

    Returns
    -------
    ET.ElementTree
      New XML document

    """
    time_now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    imagery_metadata = ET.Element("ImageryMetadata")
    ET.SubElement(imagery_metadata, "ProviderProductionDateTime").text = time_now
    ET.SubElement(imagery_metadata, "DataStartDateTime").text = beginning_time
    ET.SubElement(imagery_metadata, "DataMidDateTime").text = middle_time
    ET.SubElement(imagery_metadata, "DataEndDateTime").text = ending_time
    ET.SubElement(imagery_metadata, "DataDay").text = dataday
    if partial_id:
        ET.SubElement(imagery_metadata, "PartialId").text = partial_id

    return ET.ElementTree(imagery_metadata)


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
