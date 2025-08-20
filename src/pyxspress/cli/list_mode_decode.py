"""
Xspress Mini Mk2 list mode test script

Used to test listening to the TCP sockets used to send list mode
event data from each ADC card.
"""

import click
from matplotlib import pyplot

from pyxspress.list_mode import ListModeDecoder, ListModeWriter
from pyxspress.util.util import setup_basic_logging


@click.command(
    help=("Decode files produced by the list mode listener."),
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]},
)
@click.argument("filename", required=True, type=str)
@click.option(
    "-ch",
    "--channel",
    type=int,
    default=None,
    help="Channel number (of card) or -1 for all channels",
)
@click.option(
    "-tf",
    "--time_frame",
    type=int,
    default=None,
    help="Time frame number (based on system framing). None to get all frames",
)
@click.option(
    "-o", "--output_file", type=str, default=None, help="Path to write time frame data"
)
def main(filename: str, channel: int | None, time_frame: int, output_file: str):
    logger = setup_basic_logging()

    if channel is None:
        if time_frame is None:
            logger.info("Getting event data for all channels and time frames")
        else:
            logger.info(f"Getting events for time frame {time_frame} for all channels")
    else:
        if time_frame is None:
            logger.info(f"Getting event data for all time frames for channel {channel}")
        else:
            logger.info(
                f"Getting events data for channel {channel} and time frame {time_frame}"
            )
    decoder = ListModeDecoder()

    time_frames = decoder.decode_file_into_time_frames(filename, channel=channel)

    if output_file:
        writer = ListModeWriter(output_file)
        writer.write_frames(time_frames, channel=channel)

    else:
        if channel is None:
            channel = 0

        if channel not in time_frames:
            raise ValueError(f"No time frames found for channel {channel}")

        if time_frame is None:
            time_frame = 0

        found_tf = False
        for frame in time_frames[channel]:
            if frame.time_frame == time_frame:
                found_tf = True
                # Get event and reset list
                event_list = [
                    event.event_height for event in frame.events if event.reset is False
                ]
                reset_list = [
                    event.event_height for event in frame.events if event.reset is True
                ]

                logger.info(
                    f"Channel {channel} TF {time_frame}: Plotting "
                    f"{frame.num_events} events and {frame.num_resets} resets"
                )

                # Create subplot
                figure, axes = pyplot.subplots(nrows=2, layout="constrained")
                figure.suptitle(f"Channel {channel} - time frame {frame.time_frame}")

                # Events
                axes[0].hist(
                    event_list,
                    bins=256,
                )
                axes[0].set_xlabel("Energy bin")
                axes[0].set_ylabel("Frequency")

                # Resets
                axes[1].hist(
                    reset_list,
                    bins=256,
                )
                axes[1].set_xlabel("Reset width (ticks)")
                axes[1].set_ylabel("Frequency")

                pyplot.show()

        if not found_tf:
            raise ValueError(f"Time frame {time_frame} not found")
