"""
Defines objects and functions used when interacting with ImageSets
"""
import pathlib

from typing import Dict, List, NamedTuple


class IncompleteImageSet(Exception):
    """
    Exception thrown if Pobit can not find a complete image set while processing the input
    """


class ImageSet(NamedTuple):
    """
    An ImageSet is defined as the collection of 3 related files:
      1. An image file (png, tiff, etc...)
      2. An xml file containing metadata about that image that can be interpreted by GIBS (ImageMetadata-v1.2)
      3. A world file (https://en.wikipedia.org/wiki/World_file)

    Each ImageSet also has a name which should uniquely identify this collection of 3 files.
    """
    name: str
    image: dict
    image_metadata: dict
    world_file: dict


def from_big_output(big_output: List[Dict]) -> List[ImageSet]:
    """
    Processes output from the BIG task to extract the list of ImageSets that will need to be sent to GITC.
    Type and fileName are required keys within image metadata, all others are optional.

    Parameters
    ----------
    big_output: List[Dict]
      List of dict where each dict is a CMA file dict

    Returns
    -------
    image_sets: List[ImageSet]
        A list of ImageSets extracted from the input
    """
    images = [g for g in big_output
              if g['type'] == 'browse' and g.get('subtype') in ('png', 'jpeg', 'geotiff', 'geojson', 'shapefile')]
    image_sets = []
    for image in images:
        image_name = pathlib.Path(image['fileName']).stem
        crs = image.get('output_crs')

        try:
            image_metadata = next(iter([g for g in big_output
                                        if g['type'] == 'metadata'
                                        and g.get('subtype') == 'ImageMetadata-v1.2'
                                        and pathlib.Path(g['fileName']).stem == image_name
                                        and g.get('output_crs') == crs]))
        except StopIteration as ex:
            raise IncompleteImageSet(f"Missing image metadata for {image}") from ex

        try:
            world_file = next(iter([g for g in big_output
                                    if g['type'] == 'metadata'
                                    and g.get('subtype') == 'world file'
                                    and pathlib.Path(g['fileName']).stem == image_name
                                    and g.get('output_crs') == crs]))
        except StopIteration:
            # World files are not always required
            world_file = {}

        image_set_name = f"{image_name}_{image_metadata.get('dataday', '')}"
        if crs:
            image_set_name = image_set_name + f"_{crs}"
        image_sets.append(
            ImageSet(name=image_set_name, image=image, image_metadata=image_metadata,
                     world_file=world_file))

    return image_sets


def to_cnm_product_dict(image_set: ImageSet) -> Dict:
    """
    Converts an ImageSet into a dict that is valid for the 'product' attribute of a CNM message.

    Parameters
    ----------
    image_set: ImageSet
      The ImageSet to convert

    Returns
    -------
    cnm_product: dict
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
