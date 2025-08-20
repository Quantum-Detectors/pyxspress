"""
File reader base class

Provides the API for reading HDF5 files and returning data
"""

import os
from abc import ABC, abstractmethod
from enum import Enum

import h5py
import hdf5plugin  # noqa
import numpy

from pyxspress.util import Loggable


class DatasetKey(Enum):
    """Dataset keys for channel data"""

    MCA = "mca"
    List = "raw"
    Undefined = "Undefined"


class FileReaderInterface(Loggable, ABC):
    scalers_per_channel = 9

    def __init__(self, dataset_key: DatasetKey = DatasetKey.Undefined) -> None:
        super().__init__()

        self.open = False

        # Channel file(s)
        self.file_list: list[h5py.File] = []

        # Map of file index to list of channel datasets
        self.file_datasets: dict[int, list[str]] = {}
        # Map of channel number to index in open file list
        self.channel_map_to_file_index: dict[int, int] = {}

        # File attributes
        self.num_frames = 0
        self.num_channels = 0
        self.channels: list[int] = []  # Channels we have data for
        self.dataset_key = dataset_key

        # Metadata file
        self.meta_file: h5py.File | None = None
        self.meta_file_datasets: list[str] = []

    def close_files(self) -> None:
        """Close all files"""
        for file in self.file_list:
            self.logger.debug(f"Closing {file}")
            file.close()

        if self.meta_file:
            self.meta_file.close()
            self.meta_file = None
            self.meta_file_datasets = []

        self.file_list = []

        self.file_datasets = {}
        self.channel_map_to_file_index = {}

        self.num_frames = 0
        self.num_channels = 0
        self.channels = []
        self.open = False

    def open_files(
        self, channel_file_names: list[str], meta_file_name: str | None
    ) -> bool:
        """Open a list of channel files and metadata

        Args:
            channel_files (List[str]): List of files to open
            meta_filename (Optional[str]): Additional optional metadata file

        Returns:
            bool: True if file(s) were opened successfully
        """
        # Sanity check files exist
        for file_name in channel_file_names:
            if not os.path.isfile(file_name):
                self.logger.error(f"Could not find file {file_name}. Does it exist?")
                return False

        if meta_file_name and not os.path.isfile(meta_file_name):
            self.logger.error(f"Could not find file {meta_file_name}. Does it exist?")
            return False

        # Now close any existing files
        self.close_files()

        # Channel data
        file_index = 0
        for file_name in channel_file_names:
            file = h5py.File(file_name)

            datasets = [key for key in file.keys() if self.dataset_key.value in key]
            self.file_datasets[file_index] = datasets

            channels = [
                int(dataset.replace(f"{self.dataset_key.value}_", ""))
                for dataset in datasets
            ]
            for channel in channels:
                self.channel_map_to_file_index[channel] = file_index

            self.num_channels += len(channels)
            self.channels.extend(channels)
            self.file_list.append(file)

            file_index += 1

        # Metadata
        if meta_file_name:
            self.meta_file = h5py.File(meta_file_name)
            self.meta_file_datasets = [
                key for key in self.meta_file.keys() if "scalar" in key
            ]

        self.meta_filename = meta_file_name

        # Get number of frames last after files have been opened
        self.num_frames = self.get_num_frames()

        self.logger.info(
            "Parsed files:\n"
            f" - Num channels: {self.num_channels}\n"
            f" - Num frames: {self.num_frames}\n"
            f" - Channels: {self.channels}\n"
            f" - File datasets:\n"
            f"    - {self.file_datasets}\n"
            f" - Channel to file mapping:\n"
            f"    - {self.channel_map_to_file_index}\n"
            f" - Meta datasets: {self.meta_file_datasets}"
        )

        self.open = True
        return True

    @abstractmethod
    def get_num_frames(self) -> int:
        """Get the number of time frames in the file

        Returns:
            int: _description_
        """

    @abstractmethod
    def get_channel_data(self, channels: int | list[int], frame: int) -> numpy.ndarray:
        """Get MCA data for a channel or list of channels

        Args:
            channels (Union[int, List[int]]): Channel or list of channels
            frame (int): Frame number

        Returns:
            numpy.ndarray: 1D array or 2D array depending on single or multiple
                           channels
        """

    @abstractmethod
    def get_scalar_data(
        self, channels: int | list[int], frame: int
    ) -> numpy.ndarray | None:
        """Get the scalar data for an specific frame number

        Args:
            channels (Union[int, List[int]]): Channel or channels or -1 for all
            frame (int): Frame number

        Returns:
            numpy.ndarray: Array of scalar values
        """
