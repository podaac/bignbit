"""
Defines objects and functions used when interacting with ImageSets
"""
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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


@dataclass
class ImageSet:
    """
    An ImageSet is defined as the collection of 3 related files:
      1. An image file (png, tiff, etc...)
      2. An xml file containing metadata about that image that can be interpreted by GIBS (ImageMetadata-v1.2)
      3. A world file (https://en.wikipedia.org/wiki/World_file)

    Each ImageSet also has a name which should uniquely identify this collection of 3 files.
    """
    name: str
    image: dict[str, Any] = field(default_factory=lambda: defaultdict(dict))
    image_metadata: dict[str, Any] = field(default_factory=lambda: defaultdict(dict))
    world_file: dict[str, Any] = field(default_factory=lambda: defaultdict(dict))


def build_image_sets(
        file_list: list[dict[str, Any]],
        cmr_concept_id: str,
        data_day: str
) -> list[ImageSet]:
    """
    Processes a list of files with metadata into a list of ImageSets that will need to be sent to GITC.
    Type and fileName are required keys within image metadata, all others are optional.

    Parameters
    ----------
    big_output: List[Dict]
      List of dict where each dict is a CMA file dict
    cmr_concept_id: str
      The concept id of the collection in CMR, gets appended to the ImageSet name
    data_day: str
      YYYYJJJ (JJJ = DOY) date format identifier for the midpoint datetime of the granule

    Returns
    -------
    image_sets: List[ImageSet]
        A list of ImageSets extracted from the input
    """
    image_sets: dict[str, ImageSet] = {}
    for file_meta in file_list:
        file_name = file_meta.get('filename', '') if 'filename' in file_meta else file_meta.get('fileName', '')
        extension = Path(file_name).suffix
        file_type = 'browse' if extension in BROWSE_IMAGE_EXTENSION_SUBTYPES else 'metadata'
        file_subtype: str | None = None
        if file_type == 'browse':
            file_subtype = BROWSE_IMAGE_EXTENSION_SUBTYPES.get(extension)
        elif extension.lower() in ['.pgw', '.wld']:
            file_subtype = 'world file'
        else:
            # skip the .aux.xml, it doesn't need to be sent to GIBS
            continue

        cnm_file_meta = file_meta_to_cnm_dict(file_meta, file_type, file_subtype, data_day)
        image_set_name = get_image_set_name(cnm_file_meta, cmr_concept_id)
        if image_set_name in image_sets:
            # ImageSet already created, add the image or world file to it
            if file_type == 'browse':
                image_sets[image_set_name].image = cnm_file_meta
            elif file_subtype == 'world file':
                image_sets[image_set_name].world_file = cnm_file_meta
        else:
            # Create a new ImageSet
            if file_type == 'browse':
                image_sets[image_set_name] = ImageSet(
                    name=image_set_name,
                    image=cnm_file_meta,
                )
            elif file_subtype == 'world file':
                image_sets[image_set_name] = ImageSet(
                    name=image_set_name,
                    world_file=cnm_file_meta,
                )

    image_set_list = list(image_sets.values())
    return image_set_list


def to_cnm_product_dict(image_set: ImageSet) -> dict[str, Any]:
    """
    Converts an ImageSet into a dict that is valid for the 'product' attribute of a CNM message.

    Parameters
    ----------
    image_set: ImageSet
      The ImageSet to convert

    Returns
    -------
    cnm_product: dict[str, Any]
      A dict that can be used as the 'product' attribute of a CNM message
    """
    def update_file_dict(file_dict):
        if 'uri' not in file_dict and 'key' in file_dict and 'bucket' in file_dict:
            file_dict['uri'] = f"s3://{file_dict['bucket']}/{file_dict['key']}"
        if 'name' not in file_dict and 'fileName' in file_dict:
            file_dict['name'] = file_dict['fileName']
        if 'checksumType' in file_dict:
            file_dict['checksumType'] = file_dict['checksumType'].upper()
        return file_dict

    product_files = [
        update_file_dict(image_set.image),
        update_file_dict(image_set.image_metadata)
    ]
    if image_set.world_file:
        product_files.append(update_file_dict(image_set.world_file))

    product = {
        "name": image_set.name,
        "dataVersion": "1.5",
        "files": product_files
    }

    return product


def file_meta_to_cnm_dict(
        cma_file_meta: dict[str, Any],
        file_type: str,
        subtype: str | None,
        data_day: str
) -> dict[str, Any]:
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
    dict[str, Any]
      a CNM compatible file dict
    """
    cnm_file_meta = cma_file_meta.copy()
    if 'filepath' in cnm_file_meta:
        cnm_file_meta['key'] = cnm_file_meta['filepath']
        del cnm_file_meta['filepath']
    if 'name' in cnm_file_meta:
        cnm_file_meta['fileName'] = cnm_file_meta['name']
        del cnm_file_meta['name']
    if 'path' in cnm_file_meta:
        del cnm_file_meta['path']
    if 'url_path' in cnm_file_meta:
        del cnm_file_meta['url_path']
    if 'filename' in cnm_file_meta:
        del cnm_file_meta['filename']

    cnm_file_meta['type'] = file_type
    if subtype is not None:
        cnm_file_meta['subtype'] = subtype

    # Technically variable and dataday are not CNM file attributes but BIG/pobit need them for processing
    if 'variable' not in cnm_file_meta:
        cnm_file_meta['variable'] = 'none'
    cnm_file_meta['dataday'] = data_day

    return cnm_file_meta


def get_image_set_name(
        cnm_file_meta: dict[str, Any],
        cmr_concept_id: str
) -> str:
    """
    Construct the name of an image set that gets passed to GIBS
    """
    image_name = Path(cnm_file_meta['fileName']).stem
    data_day = cnm_file_meta.get('dataday', '')
    crs = cnm_file_meta.get('output_crs')
    image_set_prefix = f"{image_name}_{data_day}"
    if crs:
        image_set_prefix = image_set_prefix + f"_{crs}"
    return f"{image_set_prefix}!{cmr_concept_id}"
