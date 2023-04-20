"""
Defines objects and functions used when interacting with ImageSets
"""
import pathlib
import typing

from typing import List


class IncompleteImageSet(Exception):
    """
    Exception thrown if Pobit can not find a complete image set while processing the input
    """


class ImageSet(typing.NamedTuple):
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


def from_big_output(big_output: List[typing.Dict]) -> List[ImageSet]:
    """
    Processes output from the BIG task to extract the list of ImageSets that will need to be sent to GITC

    Parameters
    ----------
    big_output: List[typing.Dict]
      List of dict where each dict is a CMA file dict

    Returns
    -------
    image_sets: typing.List[ImageSet]
        A list of ImageSets extracted from the input
    """
    images = [g for g in big_output
              if g['type'] == 'browse' and g['subtype'] in ('png', 'jpeg', 'geotiff', 'geojson', 'shapefile')]
    image_sets = []
    for image in images:
        image_name = pathlib.Path(image['fileName']).stem

        try:
            image_metadata = next(iter([g for g in big_output
                                        if g['type'] == 'metadata'
                                        and g['subtype'] == 'ImageMetadata-v1.2'
                                        and pathlib.Path(g['fileName']).stem == image_name]))
        except StopIteration as ex:
            raise IncompleteImageSet(f"Missing image metadata for {image}") from ex

        try:
            world_file = next(iter([g for g in big_output
                                    if g['type'] == 'metadata'
                                    and g['subtype'] == 'world file'
                                    and pathlib.Path(g['fileName']).stem == image_name]))
        except StopIteration:
            # World files are not always required
            world_file = {}

        image_sets.append(
            ImageSet(name=f"{image_name}_{image_metadata['dataday']}", image=image, image_metadata=image_metadata,
                     world_file=world_file))

    return image_sets


def to_cnm_product_dict(image_set: ImageSet) -> dict:
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
            file_dict['uri'] = f's3://{file_dict["bucket"]}/{file_dict["key"]}'
        if 'name' not in file_dict and 'fileName' in file_dict:
            file_dict['name'] = file_dict['fileName']
        return file_dict

    product = {
        "name": image_set.name,
        "dataVersion": "1.5",
        "files": [update_file_dict(image_set.image),
                  update_file_dict(image_set.image_metadata)]
    }
    if image_set.world_file:
        product["files"].append(update_file_dict(image_set.world_file))

    return product
