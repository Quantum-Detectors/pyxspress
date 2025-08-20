"""
Xspress list mode file reader module

File reader which can open HDF5 files produced in list mode by Odin.

..note::
    This only works for X3X2 list mode file formats.

"""

import numpy

from pyxspress.data import DatasetKey, FileReaderInterface


class XspressListFileReader(FileReaderInterface):
    num_scalars = 9

    def __init__(self) -> None:
        # Maximum index of data before padding per channel
        self.max_indices: dict[int, int] = {}

        super().__init__(dataset_key=DatasetKey.List)

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
            # Get time stamps for channel
            file_index = self.channel_map_to_file_index[channel]
            file = self.file_list[file_index]
            time_stamps = file[f"{self.dataset_key.value}_{channel}"][...][1::3]

            # Find last time stamp (or if there are any at all)
            nonzero_time_stamps = (time_stamps != 0).nonzero()[0]
            if len(nonzero_time_stamps) == 0:
                self.max_indices[channel] = 0
            else:
                self.max_indices[channel] = nonzero_time_stamps[-1]
                first_time = time_stamps[0]
                last_time = time_stamps[nonzero_time_stamps[-1]]
                # 200MHz clock used
                elapsed_time = (last_time - first_time) / 200e6
                self.logger.info(
                    f"Channel {channel} first time stamp: {first_time}, "
                    f"last: {last_time}, "
                    f"elapsed: {elapsed_time}s"
                )

            # Get number of time frames
            time_frames_in_channel = file[f"{self.dataset_key.value}_{channel}"][...][
                0::3
            ][self.max_indices[channel]]

            if time_frames_in_channel > num_time_frames:
                num_time_frames = time_frames_in_channel

        self.logger.info(f"Number of events per channel: {self.max_indices}")

        # Time frame numbers are 0-indexed
        return int(num_time_frames + 1)

    def get_num_frames(self) -> int:
        """Get the number of time frames in the file

        Returns:
            int: Number of frames
        """
        assert len(self.file_list) > 0, "Need to open file first"

        # Work out maximum indices for each channel
        num_time_frames = self.__set_max_indices()

        # Number of frames based on time frame of last event in first channel
        return num_time_frames

    def get_channel_data(self, channels: int | list[int], frame: int) -> numpy.ndarray:
        """Get data of a single frame for either a single channel or all channels

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
        # Get the list data
        dataset_name = f"{self.dataset_key.value}_{channel}"
        list_data = self.file_list[self.channel_map_to_file_index[channel]][
            dataset_name
        ]
        # Without [...] we get shocking read performance - must be some h5py "magic"
        time_frames = list_data[...][::3][0 : self.max_indices[channel] + 1]

        indices = (time_frames == frame).nonzero()
        if len(indices[0]) == 0:
            # No events in the time frame
            self.logger.info(f"CH{channel}: got no events for tf {frame}")
            return numpy.histogram([], bins=numpy.arange(4096))[0]

        start = indices[0][0]
        stop = indices[0][-1]
        self.logger.info(f"CH{channel}: frame {frame} indices: {start}-{stop}")

        # Now get corresponding event heights
        event_heights = list_data[...][2::3][start : stop + 1]
        self.logger.info(f"CH{channel}: got {len(event_heights)} events for tf {frame}")

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
