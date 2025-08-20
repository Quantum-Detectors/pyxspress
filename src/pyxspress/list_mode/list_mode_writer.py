"""
List mode writer

Used to write list mode time frames to HDF5 files in the expected
format that will be used for Odin.
"""

import os

import h5py
import numpy

from pyxspress.list_mode.list_mode_decoder import TimeFrame
from pyxspress.util import Loggable


class ListModeWriter(Loggable):
    def __init__(self, file_path: str):
        super().__init__()

        if os.path.exists(file_path):
            raise ValueError(f"Path {file_path} already exists")

        self.file_path = file_path
        self.file = h5py.File(self.file_path, "w")

    def write_frame(self, channel: int, frame: TimeFrame):
        """Write events from a single frame to the HDF5 file

        The events will be added to the dataset for a specific channel

        Args:
            channel (int): Channel number on ADC card
            frame (TimeFrame): Time frame
        """
        self.logger.debug(f"Writing frame {frame.time_frame}")

        # Create the numpy array with the correct structure
        row_data_type = numpy.dtype(
            [
                ("Time frame", numpy.uint64),
                ("Time stamp", numpy.uint64),
                ("Event height", numpy.uint16),
                ("Reset", bool),
            ]
        )
        frame_data = numpy.empty(len(frame.events), dtype=row_data_type)
        frame_data[:]["Time frame"] = frame.time_frame
        frame_data[:]["Time stamp"] = [event.time_stamp for event in frame.events]
        frame_data[:]["Event height"] = [event.event_height for event in frame.events]
        frame_data[:]["Reset"] = [event.reset for event in frame.events]

        dataset_name = f"ch{channel}-events"
        if dataset_name not in self.file:
            # Dataset doesn't exist
            self.file.create_dataset(dataset_name, data=frame_data, maxshape=(None,))

        else:
            # Extend existing dataset
            dataset = self.file[dataset_name]
            dataset.resize(dataset.size + frame_data.shape[0], axis=0)
            dataset[-frame_data.shape[0] :] = frame_data

        self.logger.info(f"Wrote frame {frame.time_frame} to file")

    def write_frames(
        self, frames: dict[int, list[TimeFrame]], channel: int | None = None
    ) -> bool:
        """Write multiple frames from the HDF5 file.

        Frames should be provided as a dictionary mapping the channel number
        to a list of time frames.

        Args:
            frames (Dict[int, List[TimeFrame]]): Time frames dictionary
            channel (Optional[int], optional): Only write for specified channel.
                                               Defaults to None.

        Returns:
            bool: True if file writing was successful
        """
        # Write all channels
        if channel is None:
            for channel in frames:
                self.logger.info(
                    f"Writing {len(frames[channel])} frames for channel {channel}"
                )
                for frame in frames[channel]:
                    self.write_frame(channel, frame)

        # Single channel
        else:
            if channel not in frames:
                self.logger.error(
                    f"Channel {channel} not found in frames list {list(frames)}"
                )
                return False

            self.logger.info(
                f"Writing {len(frames[channel])} frames for channel {channel}"
            )
            for frame in frames[channel]:
                self.write_frame(channel, frame)

        return True
