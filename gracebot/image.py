import logging
import os
from io import BytesIO

import numpy as np
import requests
from PIL import Image, PngImagePlugin


class ImageFromUrl(object):
    """
    Get an image from an URL and optionally crop it.
    """

    def __init__(self, url: str, border: int = 5) -> None:
        self.url = url
        self.event_id = self.url.split("/")[-3]
        self.filename = self.get_filename()

        self.dir = f"gracebot/img/{self.event_id}"
        create_dir(self.dir)

        self._path = f"{self.dir}/{self.filename}"
        if not os.path.isfile(self._path):
            logging.info(
                f"Getting event image, because no image was found at {self._path}."
            )
            self.img = self.from_url()
            self.reduce_whitespace(border)
            self.img.save(self.path)
        else:
            logging.info(f"Serving image from {self._path}")

    @property
    def path(self) -> str:
        return self._path

    def get_filename(self) -> str:
        """
        Return valid filename for image.

        If there are multiple files in the database they append it with
        ',{number}'. For example image.png,0. This method will put the `number`
        between the filename and the extension. Thus 'image.png,0' becomes
        'image0.png'.

        Returns
        -------
        str
            Converted filename.
        """
        fname = self.url.split("/")[-1]
        if "," in fname:
            _fname, _i = fname.split(",")
            _split_fname = _fname.split(".")
            _name = _split_fname[0]
            _extension = _split_fname[-1]
            return _name + _i + "." + _extension
        else:
            return fname

    def from_url(self) -> PngImagePlugin.PngImageFile:
        """
        Loads image from url.

        Returns
        -------
        Image
            PIL Image object.

        Source
        ------
        https://stackoverflow.com/a/23489503/6329629
        """
        response = requests.get(self.url)
        img = Image.open(BytesIO(response.content))

        return img

    def reduce_whitespace(self, border: int = 5) -> None:
        """
        Reduce the amount of whitespace around an image.

        Parameters
        ----------
        border : int
            The amount of white space in pixels you want on all sides. Default
            is 5.

        Returns
        -------
        None

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

        self.img = self.img.crop(larger_box)


def add_whitespace(bounding_box: list, border: int = 5) -> list:
    """
    Add white space to an existing bounding box.

    Parameters
    ----------
    bounding_box : list
        Four corner coordinates of the cropped image without whitespace.
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


def create_dir(directory) -> None:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError:
            logging.error(f"Creation of the directory {directory} failed")
