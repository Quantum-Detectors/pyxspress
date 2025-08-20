import h5py

from .file_reader_interface import FileReaderInterface
from .xspress_list_file_reader import XspressListFileReader
from .xspress_mca_file_reader import XspressMCAFileReader


def get_file_reader(file_name: str) -> FileReaderInterface:
    """Get the appropriate file reader for target file

    Args:
        file_name (str): A file containing the channel data
                            in either list mode or MCA mode

    Returns:
        FileReaderInterface: File reader interface to use

    """
    # Need to open the file and find out datasets
    file = h5py.File(file_name)
    num_mca_datasets = len([key for key in file.keys() if "mca" in key])
    file.close()

    if num_mca_datasets > 0:
        return XspressMCAFileReader()
    else:
        return XspressListFileReader()
