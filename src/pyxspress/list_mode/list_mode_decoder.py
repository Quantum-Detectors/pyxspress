"""
Xspress Mini Mk2 list mode decoder

Decodes a binary stream into list mode events
"""

from pyxspress.util import Loggable


class Event:
    def __init__(
        self,
        time_frame: int,
        time_stamp: int,
        event_height: int,
        ttl_a: bool,
        ttl_b: bool,
        reset: bool,
        eof: bool,
    ):
        self.time_frame = time_frame
        self.time_stamp = time_stamp
        self.event_height = event_height
        self.ttl_a = ttl_a
        self.ttl_b = ttl_b
        self.reset = reset
        self.eof = eof

    def __repr__(self):
        return (
            f"Event({self.time_frame}, {self.time_stamp}, {self.event_height}, "
            f"{self.ttl_a}, {self.ttl_b}, {self.reset}, {self.eof})"
        )


class TcpFrame:
    def __init__(self, channel: int = -1, acquisition_number: int = -1) -> None:
        """TCP frame

        Generated when decoding a TCP packet into events

        Args:
            channel (int, optional): Channel number. Defaults to -1.
            acquisition_number (int, optional): Acquisition number. Defaults to -1.
        """
        # These are set after
        self.acquisition_number = acquisition_number
        self.channel = channel
        self.events: list[Event] = []
        self.num_resets = 0
        self.num_events = 0

    def add_event(self, event: Event):
        self.events.append(event)


class TimeFrame:
    def __init__(
        self,
        acquisition_number: int,
        channel: int,
        time_frame: int,
    ):
        """Time Frame

        Used to hold events related to a single time frame and channel

        Args:
            acquisition_number (int): Acquisition number
            channel (int): Channel number
            time_frame (int): Time frame number
        """
        self.acquisition_number = acquisition_number
        self.channel = channel
        self.time_frame = time_frame
        self.events: list[Event] = []
        self.num_resets = 0
        self.num_events = 0

    def add_event(self, event: Event):
        self.events.append(event)


class ListModeDecoder(Loggable):
    frame_size_bytes = 8192
    frame_header_fields = 16

    def __init__(self):
        super().__init__()

    def decode_file_into_time_frames(
        self, file_path: str, channel: int | None = None
    ) -> dict[int, list[TimeFrame]]:
        """Decode a file into a list of time frames

        Args:
            file_path (str): Path to file containing binary data from ListModeListener
            channel (int, optional): Channel to get time frames for.

        Returns:
            Dict[List[TimeFrame]]: A dictionary of time frames by channel
        """
        self.logger.info(f"Opening file {file_path} for decoding")
        with open(file_path, "rb") as input_file:
            data = input_file.read()

        num_frames = len(data) // self.frame_size_bytes
        self.logger.info(f"Total TCP frames read: {num_frames}")

        time_frames: dict[int, list[TimeFrame]] = {}

        if channel is not None:
            self.logger.info(f"Decoding time frames for channel {channel}")
        else:
            self.logger.info("Decoding time frames for all channels")

        # Iterate over each TCP frame and collect them all
        for frame in range(num_frames):
            # Decode the TCP frame
            frame_start = frame * self.frame_size_bytes
            frame_end = (frame + 1) * self.frame_size_bytes
            tcp_frame = self.decode_tcp_frame(
                data[frame_start:frame_end], requested_channel=channel
            )

            # Format events into time frames
            if tcp_frame and tcp_frame.num_events > 0:
                tcp_chan = tcp_frame.channel
                if tcp_chan not in time_frames:
                    # Add the channel to the dictionary
                    time_frames[tcp_chan] = []
                    time_frames[tcp_chan].append(
                        TimeFrame(
                            tcp_frame.acquisition_number,
                            tcp_chan,
                            tcp_frame.events[0].time_frame,
                        )
                    )

                remaining_tcp_frame_events = len(tcp_frame.events)
                tcp_frame_event_index = 0
                while remaining_tcp_frame_events > 0:
                    # Add events matching current time frame
                    current_time_frame_events = [
                        event
                        for event in tcp_frame.events
                        if event.time_frame == time_frames[tcp_chan][-1].time_frame
                    ]
                    time_frames[tcp_chan][-1].events.extend(current_time_frame_events)
                    time_frames[tcp_chan][-1].num_resets += tcp_frame.num_resets
                    time_frames[tcp_chan][-1].num_events += tcp_frame.num_events

                    # Check for remaining events
                    # (these will be from a different time frame)
                    remaining_tcp_frame_events -= len(current_time_frame_events)
                    if remaining_tcp_frame_events > 0:
                        # Add new time frame
                        tcp_frame_event_index += len(current_time_frame_events)
                        new_time_frame = tcp_frame.events[
                            tcp_frame_event_index
                        ].time_frame

                        # Sanity check
                        if new_time_frame < time_frames[tcp_chan][-1].time_frame:
                            self.logger.error(
                                f"New time frame number {new_time_frame} is less"
                                "than current time frame being processed "
                                f"({time_frames[tcp_chan][-1].time_frame})"
                            )

                        time_frames[tcp_chan].append(
                            TimeFrame(
                                tcp_frame.acquisition_number,
                                tcp_chan,
                                new_time_frame,
                            )
                        )
                        time_frames[tcp_chan][-1].num_resets = tcp_frame.num_resets
                        time_frames[tcp_chan][-1].num_events = tcp_frame.num_events

        self.logger.info(f"Number of channels: {len(time_frames)}")
        for channel in time_frames:
            self.logger.info(f"Channel {channel} frames: {len(time_frames[channel])}")

            for time_frame in time_frames[channel]:
                self.logger.info(
                    f" - frame {time_frame.time_frame}: "
                    f"{time_frame.num_events} events, "
                    f"{time_frame.num_resets} resets, "
                    f"{len(time_frame.events)} total events"
                )

        return time_frames

    def decode_tcp_frame(
        self,
        frame_data: bytes,
        requested_channel: int | None = None,
    ) -> TcpFrame | None:
        """Decode a single TCP frame of data

        This will return nothing if the frame does not match the requested channel or
        time frame

        Args:
            frame_data (bytes): Frame data bytes (should be 8192 long)
            requested_channel (Optional[int], optional): Optionally check frame is for a
                                                        specific card channel. Defaults
                                                        to None.

        Returns:
            Optional[TcpFrame]: Processed TCP frame
        """
        assert len(frame_data) == self.frame_size_bytes, (
            f"Expected {self.frame_size_bytes} bytes for frame, got {len(frame_data)}"
        )

        num_fields = len(frame_data) // 2

        num_padding_events = 0
        num_dummy_events = 0
        num_eof_events = 0

        # Components of attributes
        # hist_address_high = -1
        # hist_address_middle = -1

        time_frame_lowest = 0
        time_frame_2nd_lowest = 0
        time_frame_3rd_lowest = 0
        time_frame_4th_lowest = 0
        time_frame_5th_lowest = 0
        time_frame_highest = 0

        time_stamp_lowest = 0
        time_stamp_2nd_lowest = 0
        time_stamp_3rd_lowest = 0
        time_stamp_highest = 0

        # Attributes
        # histogram_address = 0
        end_of_frame = 0
        ttl_a = 0
        ttl_b = 0
        dummy_event = 0
        time_frame = 0
        channel_number = -1
        time_stamp = 0

        num_events = 0
        num_resets = 0

        # Create new TCP frame
        frame = TcpFrame()

        # Read all of the fields and process
        for field in range(num_fields):
            field_value = int.from_bytes(
                frame_data[2 * field : 2 * field + 2], "little"
            )
            id = field_value >> 12
            value = field_value & 0xFFF

            match id:
                case 1:
                    frame.acquisition_number = value
                case 2:
                    # Middle part of histogram address - 0 except in debug
                    # hist_address_middle = value
                    pass
                case 3:
                    # High part of histogram address - 0 except in debug
                    # hist_address_high = value
                    pass
                case 4:
                    end_of_frame = value & 0x1
                    ttl_a = value & 0x2
                    ttl_b = value & 0x4
                    dummy_event = value & 0x8
                    time_frame_lowest = value >> 4
                case 5:
                    time_frame_2nd_lowest = value
                case 6:
                    time_frame_3rd_lowest = value
                case 7:
                    time_frame_4th_lowest = value
                case 8:
                    time_frame_5th_lowest = value
                case 9:
                    time_frame_highest = value & 0xFF
                    frame.channel = value >> 8

                    # Check if we want a specific channel
                    if requested_channel is not None:
                        if channel_number != requested_channel:
                            return None

                case 10:
                    time_stamp_lowest = value
                case 11:
                    time_stamp_2nd_lowest = value
                case 12:
                    time_stamp_3rd_lowest = value
                case 13:
                    time_stamp_highest = value
                case 15:
                    # Track number of padded fields per frame
                    num_padding_events += 1
                case 14:
                    # Reset found
                    if not dummy_event and not end_of_frame:
                        time_frame = (
                            time_frame_lowest
                            + (time_frame_2nd_lowest << 8)
                            + (time_frame_3rd_lowest << 20)
                            + (time_frame_4th_lowest << 32)
                            + (time_frame_5th_lowest << 44)
                            + (time_frame_highest << 56)
                        )

                        time_stamp = (
                            time_stamp_lowest
                            + (time_stamp_2nd_lowest << 12)
                            + (time_stamp_3rd_lowest << 24)
                            + (time_stamp_highest << 36)
                        )

                        frame.add_event(
                            Event(
                                time_frame,
                                time_stamp,
                                value,
                                bool(ttl_a),
                                bool(ttl_b),
                                True,
                                bool(end_of_frame),
                            )
                        )

                        num_resets += 1

                case 0:
                    # Event found
                    if not dummy_event and not end_of_frame:
                        time_frame = (
                            time_frame_lowest
                            + (time_frame_2nd_lowest << 8)
                            + (time_frame_3rd_lowest << 20)
                            + (time_frame_4th_lowest << 32)
                            + (time_frame_5th_lowest << 44)
                            + (time_frame_highest << 56)
                        )

                        time_stamp = (
                            time_stamp_lowest
                            + (time_stamp_2nd_lowest << 12)
                            + (time_stamp_3rd_lowest << 24)
                            + (time_stamp_highest << 36)
                        )

                        frame.add_event(
                            Event(
                                time_frame,
                                time_stamp,
                                value,
                                bool(ttl_a),
                                bool(ttl_b),
                                False,
                                bool(end_of_frame),
                            )
                        )

                        num_events += 1

        self.logger.debug(
            "FRAME COMPLETE\n"
            f"Acquisition number: {frame.acquisition_number}\n"
            f"Channel: {frame.channel}\n"
            f"Number of dummy events: {num_dummy_events}\n"
            f"Number of eof events: {num_eof_events}\n"
            f"Padded fields: {num_padding_events}\n"
            f"Real events: {num_events}\n"
            f"Resets: {num_resets}"
        )

        frame.num_resets = num_resets
        frame.num_events = num_events
        return frame
