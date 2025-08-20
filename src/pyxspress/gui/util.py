"""
GUI utility module

"""

import os
from pathlib import Path


def get_image_path(file_name: str) -> Path:
    """Get the full image path for an image located in the module's images directory.

    Args:
        file_name (str): File name of image including extension

    Returns:
        Path: Full path to image
    """
    return Path(os.path.dirname(os.path.realpath(__file__))) / f"{file_name}"
