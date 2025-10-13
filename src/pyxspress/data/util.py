import glob
import os

import h5py

from pyxspress.util import get_module_logger

from .file_reader_interface import FileReaderInterface
from .xspress_list_file_reader import XspressListFileReader
from .xspress_mca_file_reader import XspressMCAFileReader

logger = get_module_logger(sub_module="data.util")


def get_file_reader(file_name: str) -> FileReaderInterface:
    """Get the appropriate file reader for target file

    Args:
        file_name (str): Either an MCA/list mode HDF5 file or a metadata file
                         with accompanying MCA/list mode HDF5 files

    Returns:
        FileReaderInterface: File reader interface to use

    """
    # Check if we have been given a metadata file.
    if "_meta.h5" in file_name:
        data_files, _ = get_matching_xspress_files(file_name)
        if len(data_files) == 0:
            raise FileNotFoundError(
                "No data files found to determine file reader needed"
            )

        # We need to use a data file to work out correct file reader
        file_name = data_files[0]

    # Need to open the file and find out datasets
    file = h5py.File(file_name)
    num_mca_datasets = len([key for key in file.keys() if "mca" in key])
    file.close()

    if num_mca_datasets > 0:
        return XspressMCAFileReader()
    else:
        return XspressListFileReader()


def get_matching_xspress_files(
    file_name: str, suffix_pattern: str = "_000000.h5"
) -> tuple[list[str], str | None]:
    """Get a list of matching Xspress files based on the file name and
    suffix pattern.

    Args:
        file_name (str): File name of one of the Xspress HDF5 files
        suffix_pattern (str, optional): Pattern to match to. Defaults to "_000000.h5",
                                        which is the default for Odin

    Returns:
        tuple[list[str], str | None]: Tuple of list of matching file names (including
                                      the original) and the metadata file or just
                                      the original file if no matching files were found.
    """
    meta_file: str | None = None

    # Work out what file prefix we need to use to search
    if suffix_pattern in file_name:
        file_prefix = file_name.split(suffix_pattern)[0][:-2]
    elif "_meta.h5" in file_name:
        file_prefix = file_name.split("_meta.h5")[0]
    else:
        logger.info("No pattern found to search with")
        return [file_name], None

    logger.info(f"File prefix: {file_prefix}")
    file_pattern = f"{file_prefix}*{suffix_pattern}"
    logger.info(f"Looking for files matching pattern: {file_pattern}")
    file_list = sorted(glob.glob(file_pattern))
    logger.info(f"Found files: {file_list}")
    if len(file_list) == 0:
        return [], None

    # Metadata file
    meta_file_name = f"{file_prefix}_meta.h5"
    logger.info(f"Looking for metadata file: {meta_file_name}")
    if os.path.exists(meta_file_name):
        logger.info(f"Found metadata file: {meta_file_name}")
        meta_file = meta_file_name

    return file_list, meta_file
