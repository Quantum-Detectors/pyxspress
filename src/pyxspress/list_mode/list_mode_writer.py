"""
List mode writer

Used to write list mode time frames to HDF5 files in the expected
format that will be used for Odin.
"""

import os
from time import time

import h5py
import numpy
from rich.progress import track

from pyxspress.data.xspress_list_file_reader import ListDataset
from pyxspress.list_mode.list_mode_decoder import TimeFrame
from pyxspress.util import Loggable


class ListModeWriter(Loggable):
    def __init__(self, file_path: str):
        super().__init__()

        if os.path.exists(file_path):
            raise ValueError(f"Path {file_path} already exists")

        self.file_path = file_path
        self.file = h5py.File(self.file_path, "w")

    def __create_dataset(self, channel: int, dataset: ListDataset, size: int) -> None:
        # Get full dataset name
        dataset_name = f"ch{channel}_{dataset.value}"

        if dataset_name in self.file:
            self.logger.warning(f"Dataset {dataset} already exists")
            return

        dataset_type: type[numpy.unsignedinteger]
        match dataset:
            case ListDataset.TimeFrame | ListDataset.TimeStamp:
                dataset_type = numpy.uint64
            case ListDataset.EventHeight:
                dataset_type = numpy.uint16
            case ListDataset.ResetFlag:
                dataset_type = numpy.uint8

        self.file.create_dataset(dataset_name, shape=(size,), dtype=dataset_type)

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
        start_time = time()

        # Write all channels
        if channel is None:
            for channel in frames:
                self.write_frames(frames, channel=channel)

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
            # Create datasets with correct size
            total_channel_events = 0
            for frame in frames[channel]:
                total_channel_events += len(frame.events)

            self.logger.info(f"Channel {channel} total events: {total_channel_events}")
            self.__create_dataset(
                channel, ListDataset.TimeFrame, size=total_channel_events
            )
            self.__create_dataset(
                channel, ListDataset.TimeStamp, size=total_channel_events
            )
            self.__create_dataset(
                channel, ListDataset.EventHeight, size=total_channel_events
            )
            self.__create_dataset(
                channel, ListDataset.ResetFlag, size=total_channel_events
            )

            timestamp_dataset = f"ch{channel}_{ListDataset.TimeStamp.value}"
            timeframe_dataset = f"ch{channel}_{ListDataset.TimeFrame.value}"
            event_height_dataset = f"ch{channel}_{ListDataset.EventHeight.value}"
            reset_flag_dataset = f"ch{channel}_{ListDataset.ResetFlag.value}"

            # Create initial buffers
            buffer_size = 1000000
            events_in_buffer = 0
            timestamp_buffer = numpy.empty(buffer_size, dtype=numpy.uint64)
            timeframe_buffer = numpy.empty(buffer_size, dtype=numpy.uint64)
            event_height_buffer = numpy.empty(buffer_size, dtype=numpy.uint16)
            reset_flag_buffer = numpy.empty(buffer_size, dtype=numpy.uint8)

            # Track remaning events when buffer is full
            remaining_events = 0

            # Track file index
            file_index = 0
            # for frame in frames[channel]:
            for frame in track(frames[channel], description="Writing..."):
                # Buffer up events
                num_events = len(frame.events)
                if events_in_buffer + num_events <= buffer_size:
                    # Can fit all events from frame into our buffer
                    timestamp_buffer[
                        events_in_buffer : events_in_buffer + num_events
                    ] = [event.time_stamp for event in frame.events]
                    timeframe_buffer[
                        events_in_buffer : events_in_buffer + num_events
                    ] = [event.time_frame for event in frame.events]
                    event_height_buffer[
                        events_in_buffer : events_in_buffer + num_events
                    ] = [event.event_height for event in frame.events]
                    reset_flag_buffer[
                        events_in_buffer : events_in_buffer + num_events
                    ] = [event.reset for event in frame.events]

                    events_in_buffer += num_events
                else:
                    # Can only fit some of the events - fill up the current
                    # buffer and track the remainder
                    buffer_space = buffer_size - events_in_buffer
                    self.logger.debug(f"Filling up to buffer space: {buffer_space}")

                    timestamp_buffer[
                        events_in_buffer : events_in_buffer + buffer_space
                    ] = [event.time_stamp for event in frame.events[:buffer_space]]
                    timeframe_buffer[
                        events_in_buffer : events_in_buffer + buffer_space
                    ] = [event.time_frame for event in frame.events[:buffer_space]]
                    event_height_buffer[
                        events_in_buffer : events_in_buffer + buffer_space
                    ] = [event.event_height for event in frame.events[:buffer_space]]
                    reset_flag_buffer[
                        events_in_buffer : events_in_buffer + buffer_space
                    ] = [event.reset for event in frame.events[:buffer_space]]

                    events_in_buffer += buffer_space
                    remaining_events = num_events - buffer_space
                    self.logger.debug(f"Remaining events: {remaining_events}")

                # Check if buffer is full
                if events_in_buffer == buffer_size:
                    self.logger.debug("Buffer is full")

                    # Write to file
                    self.file[timestamp_dataset][
                        file_index : file_index + buffer_size
                    ] = timestamp_buffer
                    self.file[timeframe_dataset][
                        file_index : file_index + buffer_size
                    ] = timeframe_buffer
                    self.file[event_height_dataset][
                        file_index : file_index + buffer_size
                    ] = event_height_buffer
                    self.file[reset_flag_dataset][
                        file_index : file_index + buffer_size
                    ] = reset_flag_buffer
                    file_index += buffer_size

                    # Create next buffers
                    events_in_buffer = 0
                    timestamp_buffer = numpy.empty(buffer_size, dtype=numpy.uint64)
                    timeframe_buffer = numpy.empty(buffer_size, dtype=numpy.uint64)
                    event_height_buffer = numpy.empty(buffer_size, dtype=numpy.uint16)
                    reset_flag_buffer = numpy.empty(buffer_size, dtype=numpy.uint8)

                    # Check for remaining events left over from filling buffer
                    if remaining_events > 0:
                        self.logger.debug(
                            f"Adding remaining {remaining_events} events to new buffer"
                        )

                        timestamp_buffer[0:remaining_events] = [
                            event.time_stamp
                            for event in frame.events[-remaining_events:]
                        ]
                        timeframe_buffer[0:remaining_events] = [
                            event.time_frame
                            for event in frame.events[-remaining_events:]
                        ]
                        event_height_buffer[0:remaining_events] = [
                            event.event_height
                            for event in frame.events[-remaining_events:]
                        ]
                        reset_flag_buffer[0:remaining_events] = [
                            event.reset for event in frame.events[-remaining_events:]
                        ]

                        events_in_buffer += remaining_events
                        remaining_events = 0
                        self.logger.debug(
                            f"Remaining events filled: {events_in_buffer}"
                        )

                        # TODO: what to do if number of events exceeds buffer size?

            # We have finished iterating through all frames but we may still
            # have events left in the buffer
            if events_in_buffer > 0:
                self.logger.debug(f"Writing remaining {events_in_buffer} events")

                self.file[timestamp_dataset][
                    file_index : file_index + events_in_buffer
                ] = timestamp_buffer[:events_in_buffer]
                self.file[timeframe_dataset][
                    file_index : file_index + events_in_buffer
                ] = timeframe_buffer[:events_in_buffer]
                self.file[event_height_dataset][
                    file_index : file_index + events_in_buffer
                ] = event_height_buffer[:events_in_buffer]
                self.file[reset_flag_dataset][
                    file_index : file_index + events_in_buffer
                ] = reset_flag_buffer[:events_in_buffer]

        elapsed_time = time() - start_time
        self.logger.info(f"Wrote in {elapsed_time:<.3f}s")

        return True
