"""
Xspress MCA file reader module

File reader which can open HDF5 files produced in MCA mode by Odin
"""

import h5py
import numpy

from pyxspress.data import DatasetKey, FileReaderInterface


class XspressMCAFileReader(FileReaderInterface):
    def __init__(self) -> None:
        super().__init__(dataset_key=DatasetKey.MCA)

    def open_data_file(self, file_index: int, file_name: str):
        """Open a single data file (i.e. not metadata)

        This should parse the files and:

        - Get the list of channels
        - Add number of channels in file to overall sum
        - Set the mapping of channel to file index
        - Append file to file list

        Args:
            file_index (int): Index of file in list
            file_name (str): File name
        """
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

    def set_num_frames(self):
        """Set the number of time frames"""
        assert len(self.file_list) > 0, "Need to open file first"
        # Number of frames from first file and first dataset
        self.num_frames = len(self.file_list[0][self.file_datasets[0][0]])

    def get_channel_data(self, channels: int | list[int], frame: int) -> numpy.ndarray:
        """Get data of a single frame for either a single channel or all channels

        This is zero-indexed (i.e. 0 is the first frame and channel)

        Args:
            channels (Union[int, List[int]]): Channel or list of channels
            frame (int): Frame number

        Returns:
            numpy.ndarray: Data array
        """
        if not self.open:
            self.logger.error(
                f"No file(s) open to get data for frame {frame}, channel {channels}"
            )

        self.logger.debug(f"Getting data for frame {frame}, channels {channels}")

        # List of channels
        if isinstance(channels, list):
            if len(channels) == 1:
                return self.get_channel_data(channels[0], frame)

            data = numpy.vstack([self.get_channel_data(ch, frame) for ch in channels])
            self.logger.debug(f"Got data of shape {data.shape}")
            return data

        # Single channel
        else:
            if channels in self.channel_map_to_file_index:
                dataset_name = f"{self.dataset_key.value}_{channels}"
                self.logger.debug(
                    f"Getting channel {channels} from file index "
                    f"{self.channel_map_to_file_index[channels]}"
                )
                return self.file_list[self.channel_map_to_file_index[channels]][
                    dataset_name
                ][frame, 0, :]
            else:
                self.logger.error(f"Invalid channel {channels}")
                return numpy.array([0, 0])

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
        if self.meta_file is None:
            # No scalar file to read from
            return None

        self.logger.debug(
            f"Getting scalar values for frame {frame} and channels {channels}"
        )
        num_scalers = 9

        if channels == -1:
            data = numpy.empty((self.num_channels, num_scalers))
            for channel in range(self.num_channels):
                data[channel, :] = self.get_scalar_data(channel, frame)

        elif isinstance(channels, list):
            if len(channels) == 1:
                return self.get_scalar_data(channels[0], frame)

            data = numpy.empty((len(channels), num_scalers))
            row_index = 0
            for channel in channels:
                data[row_index, :] = self.get_scalar_data(channel, frame)
                row_index += 1

        else:
            data = numpy.empty(self.scalers_per_channel)
            for scalar_num in range(self.scalers_per_channel):
                dataset_name = f"scalar_{scalar_num}"
                data[scalar_num] = self.meta_file[dataset_name][frame][channels]

        return data
