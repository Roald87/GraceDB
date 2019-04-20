from io import BytesIO
from typing import List

import numpy as np
import requests
from PIL import Image

BoundingBox = List[int]


class ImageFromUrl(object):
    """
    Get an image from an URL and optionally crop it.
    """

    def __init__(self, url: str):
        self.img = self.from_url(url)

    def from_url(self, url: str) -> Image:
        """
        Loads image from url.

        Parameters
        ----------
        url : str
            URL of the image.

        Returns
        -------
        Image
            PIL Image object.

        Source
        ------
        https://stackoverflow.com/a/23489503/6329629

        """
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))

        return img

    def reduce_whitespace(self, border: int = 5) -> str:
        """
        Reduce the amount of whitespace around an image.

        Parameters
        ----------
        border : int
            The amount of white space in pixels you want on all sides. Default
            is 5.

        Returns
        -------
        Local filename of the cropped image.

        Source
        ------
        https://stackoverflow.com/a/23489503/6329629


        """
        if self.img is None:
            raise FileExistsError("Load an image first with from_url.")

        pix = np.asarray(self.img)

        pix = pix[:, :, 0:3]  # Drop the alpha channel
        idx = np.where(pix - 255)[0:2]  # Drop the color when finding edges
        bbox = list(map(min, idx))[::-1] + list(map(max, idx))[::-1]
        larger_box = add_whitespace(bbox, border)

        region = self.img.crop(larger_box)
        image_fname = 'cropped_image.png'
        region.save(image_fname)

        return image_fname


def add_whitespace(bounding_box: BoundingBox, border: int = 5) -> BoundingBox:
    """

    Parameters
    ----------
    bounding_box : BoundingBox
        A list of length 4 with the corner coordinates of the cropped image
        without whitespace.
    border : int
        The amount of whitespace you want to add on all sides.

    Returns
    -------
    Bounding box with increased whitespace.

    """
    assert len(bounding_box) == 4, "Bounding box can only have 4 corners"

    larger_box = []
    for i, corner in enumerate(bounding_box):
        if i < 2:
            larger_box.append(corner - border)
        else:
            larger_box.append(corner + border)

    return larger_box
