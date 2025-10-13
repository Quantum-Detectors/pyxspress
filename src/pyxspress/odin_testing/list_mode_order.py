"""
List mode test module

Used to check HDF5 files produced by Odin list mode
"""

from pyxspress.data.xspress_list_file_reader import ListDataset, XspressListFileReader
from pyxspress.util import get_module_logger

logger = get_module_logger("list_mode_order")


def check_time_stamp_ordering(
    file_reader: XspressListFileReader, channel: int = -1
) -> bool:
    """Check the time stamps are in chronological order

    Args:
        file_reader (XspressListFileReader): File reader with open files
        channel (int, optional): Only check specific channel, or -1 for all channels.
                                 Defaults to -1.

    Returns:
        bool: True if all in order, False if at least 1 failure
    """
    logger.info("Checking time stamp ordering")

    channel_list = file_reader.channels if channel == -1 else [channel]

    max_output = 100
    num_output = 0

    test_passed = True

    for channel in channel_list:
        logger.info(f" - checking channel {channel}")
        num_out_of_order = 0
        time_stamps = file_reader.get_channel_dataset(channel, ListDataset.TimeStamp)
        for index in range(len(time_stamps) - 1):
            # Compare to the next time stamp in the list
            if time_stamps[index + 1] < time_stamps[index]:
                num_out_of_order += 1
                test_passed = False
                # Restrict number of times we output
                if num_output < max_output:
                    logger.info(
                        f"   -> index {index + 1}: time stamp {time_stamps[index + 1]} "
                        f"lower than previous index ({time_stamps[index]})"
                    )
                    if index + 2 < len(time_stamps):
                        logger.info(
                            f"      (next index: {index + 2}: {time_stamps[index + 2]})"
                        )
                    num_output += 1

        logger.info(f"   -> num out of order: {num_out_of_order}")

    return test_passed


def check_time_frame_ordering(
    file_reader: XspressListFileReader, channel: int = -1
) -> bool:
    """Check the order of time frames for every recorded event

    Args:
        file_reader (XspressListFileReader): file reader with files set
        channel (int, optional): Only check specific channel, or -1 for all channels.
                                 Defaults to -1.

    Returns:
        bool: True if all in order, False if at least 1 failure
    """
    logger.info("Checking time frame ordering")

    test_passed = True

    channel_list = file_reader.channels if channel == -1 else [channel]
    for channel in channel_list:
        logger.info(f" - checking channel {channel}")
        time_frames = file_reader.get_channel_dataset(channel, ListDataset.TimeFrame)

        current_time_frame = 0
        index = 0

        out_of_order = False
        start_wrong_index = 0
        num_wrong_order = 0
        num_times_skipped = 0

        for time_frame in time_frames:
            if time_frame == current_time_frame + 1:
                # Sequential time frames
                current_time_frame = time_frame
                if out_of_order:
                    out_of_order = False
                    logger.info(
                        f"   -> index {index}: recovered from wrong order from "
                        f" index {start_wrong_index}"
                    )
            elif time_frame > current_time_frame + 1:
                # We jumped but this may be okay if the time frame is short compared
                # to event flux
                num_times_skipped += 1
                current_time_frame = time_frame
                if out_of_order:
                    out_of_order = False
                    logger.info(
                        f"   -> index {index}: recovered from wrong order from "
                        f" index {start_wrong_index}"
                    )
            elif time_frame != current_time_frame:
                # TF gone back time time
                logger.error(
                    f"   -> index {index}: unexpected older time frame: {time_frame} "
                    f"for current tf: {current_time_frame}"
                )
                current_time_frame = time_frame
                start_wrong_index = index
                out_of_order = True
                num_wrong_order += 1
                test_passed = False

            index += 1

        logger.info(f"   -> num out of order: {num_wrong_order}")
        logger.info(f"   -> num times skipped: {num_times_skipped}")

    return test_passed
