"""
Xspress list mode file reader module

File reader which can open HDF5 files produced in list mode by Odin.

..note::
    This only works for X3X2 list mode file formats.

"""

import re
from enum import Enum

import h5py
import numpy

from pyxspress.data import DatasetKey, FileReaderInterface


class ListDataset(Enum):
    """List mode dataset keys"""

    EventHeight = "event_height"
    TimeFrame = "time_frame"
    TimeStamp = "time_stamp"
    ResetFlag = "reset_flag"


class XspressListFileReader(FileReaderInterface):
    num_scalars = 9

    timeframe_suffix = "time_frame"
    timestamp_suffix = "time_stamp"
    event_height_suffix = "event_height"
    reset_flag_suffix = "reset_flag"

    def __init__(self) -> None:
        # Maximum index of data before padding per channel
        self.max_indices: dict[int, int] = {}

        super().__init__(dataset_key=DatasetKey.List)

    def get_channel_dataset(
        self,
        channel: int,
        dataset: ListDataset,
        start_index: int = 0,
        stop_index: int = -1,
    ) -> numpy.ndarray:
        """Get a single dataset for a specific channel

        Args:
            channel (int): Channel number
            dataset (ListDataset): Dataset to fetch
            start_index (int, optional): Only include from the first index. Defaults to
                                         0.
            stop_index (int, optional): Only include up to the stop index. If -1 then
                                        this will return up to the max index of actual
                                        data in the dataset and exclude the zero
                                        padding, or it will return all the data if this
                                        index is not yet known.

        Returns:
            numpy.ndarray: Array data
        """
        # Identify the file to read from
        file_index = self.channel_map_to_file_index[channel]
        file = self.file_list[file_index]

        # Work out actual stop index to use
        if stop_index == -1:
            # This will either be -1 if we don't know yet or the last index
            # before the 0 padding at the end. This will be set by __set_max_indices
            stop_index = self.max_indices[channel]
            if stop_index != -1:
                # Need to add one to include the last index provided
                stop_index += 1
        else:
            # Add one to include the last index provided
            stop_index = stop_index + 1

        return file[f"ch{channel}_{dataset.value}"][...][start_index:stop_index]

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

        # Filter out marker channel data for now
        ch_datasets = [ds for ds in datasets if re.match(r"^ch\d+_", ds)]

        channels = [
            self.__get_channel_from_dataset_name(dataset) for dataset in ch_datasets
        ]
        for channel in channels:
            self.channel_map_to_file_index[channel] = file_index

            # Initialise as -1 until we know where the last value is
            self.max_indices[channel] = -1

        self.num_channels += len(channels)
        self.channels.extend(channels)
        self.file_list.append(file)

    def set_num_frames(self):
        """Set the number of time frames found within the file"""
        assert len(self.file_list) > 0, "Need to open file first"

        # Work out maximum indices for each channel if we haven't already
        self.num_frames = self.__set_max_indices()

    def get_channel_data(self, channels: int | list[int], frame: int) -> numpy.ndarray:
        """Get MCA data of a single frame for either a single channel or all channels

        This is zero-indexed (i.e. 0 is the first frame and channel)

        Args:
            channels (Union[int, List[int]]): Channel or list of channels
            frame (int): Frame number

        Returns:
            numpy.ndarray: MCA histogram
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
            return self.get_single_frame(channels, frame)

    def get_single_frame(self, channel: int, frame: int) -> numpy.ndarray:
        """Get a single frame of data

        Produces a single MCA frame from list mode data

        Args:
            channel (int): Channel number
            frame (int): Frame number
        """
        # Work out indices matching desired our time frame
        time_frames = self.get_channel_dataset(channel, ListDataset.TimeFrame)

        if frame == 0:
            # The end of the HDF5 file is padded with zeroes, so we need to
            # exclude these from the zeroth time frame
            start = 0
            if self.num_frames == 1:
                # There is only a single time frame in the data, so we can just
                # use the maximum index of the data that we found when opening
                # the file
                stop = self.max_indices[channel]
            else:
                # There is at least one more time frame, so we can find the start
                # of the next time frame and use that to work out the end of this
                # one
                next_indices = (time_frames == frame + 1).nonzero()
                if len(next_indices[0]) == 0:
                    # No events in the following time frame
                    # TODO: what happens if we have no events in the next tf,
                    #       but we do in e.g. tf + 2 or + 3 (for small time frames
                    #       and sparse events)
                    self.logger.info(
                        f"ch{channel}: got no events for next tf {frame + 1}"
                    )
                    return numpy.histogram([], bins=numpy.arange(4096))[0]

                stop = next_indices[0][0] - 1

        else:
            # Otherwise we can just find the start-stop of the time frame
            # by searching for the matching indices normally
            indices = (time_frames == frame).nonzero()
            if len(indices[0]) == 0:
                # No events in the time frame
                self.logger.info(f"ch{channel}: got no events for tf {frame}")
                return numpy.histogram([], bins=numpy.arange(4096))[0]

            start = indices[0][0]
            stop = indices[0][-1]

        self.logger.info(f"ch{channel}: frame {frame} indices: {start}-{stop}")

        # Now get corresponding event heights
        event_heights = self.get_channel_dataset(
            channel, ListDataset.EventHeight, start_index=start, stop_index=stop
        )
        self.logger.info(
            f"ch{channel}: got {len(event_heights)} total events for tf {frame}"
        )

        # Remove reset events
        reset_flags = self.get_channel_dataset(
            channel, ListDataset.ResetFlag, start_index=start, stop_index=stop
        )
        non_reset_indices = (reset_flags == 0).nonzero()
        self.logger.info(
            f"ch{channel}: got {len(non_reset_indices[0])} real events "
            "after removing resets"
        )
        event_heights = event_heights[non_reset_indices]

        # Produce histogram
        histogram = numpy.histogram(event_heights, bins=numpy.arange(4096))
        return histogram[0]

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
        # TODO: implement when ready
        return None

    def __set_max_indices(self) -> int:
        """Set the maximum data index for each channel before padding

        This is the number of events for each channel.

        This then returns the maximum number of time frames based on the largest channel

        Returns:
            int: Number of time frames
        """
        num_time_frames = 0
        self.logger.info("Locating padding for each channel")
        for channel in self.channels:
            # Find last time stamp (or if there are any at all)
            time_stamps = self.get_channel_dataset(channel, ListDataset.TimeStamp)
            nonzero_time_stamps = (time_stamps != 0).nonzero()[0]
            if len(nonzero_time_stamps) == 0:
                self.max_indices[channel] = 0
            else:
                self.max_indices[channel] = nonzero_time_stamps[-1]
                first_time = time_stamps[0]
                last_time = time_stamps[nonzero_time_stamps[-1]]
                # 200MHz clock used
                elapsed_time = (last_time - first_time) / 200e6
                self.logger.debug(
                    f"Channel {channel} first time stamp: {first_time}, "
                    f"last: {last_time}, "
                    f"elapsed: {elapsed_time}s"
                )

            self.logger.debug(
                f"Channel {channel} max index: {self.max_indices[channel]}"
            )

            # Get number of time frames
            time_frames = self.get_channel_dataset(channel, ListDataset.TimeFrame)
            time_frames_in_channel = int(time_frames[-1] + 1)
            self.logger.info(
                f"Time frames in channel {channel}: {time_frames_in_channel}"
            )
            if time_frames_in_channel > num_time_frames:
                num_time_frames = time_frames_in_channel

        self.logger.info(f"Number of events per channel: {self.max_indices}")

        return num_time_frames

    def __get_channel_from_dataset_name(self, dataset_name: str) -> int:
        """Get channel number from dataset name

        Args:
            dataset_name (str): Name of dataset

        Returns:
            int: Channel
        """
        # Format is ch<num>_event_height
        return int(
            dataset_name.replace(f"_{self.dataset_key.value}", "").replace("ch", "")
        )
