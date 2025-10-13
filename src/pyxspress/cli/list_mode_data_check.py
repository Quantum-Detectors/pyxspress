"""
Odin list mode data check

This script looks at a single acquisition based on a path to one of its HDF5 files
and checks the ordering of events across all channels or a specific channel.
"""

import click

from pyxspress.data import get_matching_xspress_files
from pyxspress.data.xspress_list_file_reader import XspressListFileReader
from pyxspress.odin_testing import check_time_frame_ordering, check_time_stamp_ordering
from pyxspress.util import setup_basic_logging


@click.command(
    help=(
        "Check data files for a single list mode acquisition by providing a "
        "path to one of the files."
    ),
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
@click.argument("file_path", required=True, type=str)
@click.option(
    "-ch",
    "--channel",
    type=int,
    default=-1,
    help="Check specific channel (or -1 for all channels)",
)
def main(file_path: str, channel: int):
    logger = setup_basic_logging()

    # Open the files
    data_files, metadata_file = get_matching_xspress_files(file_path)
    file_reader = XspressListFileReader()
    file_reader.open_files(data_files, metadata_file)

    # Check them
    passed = True
    passed &= check_time_frame_ordering(file_reader, channel=channel)
    passed &= check_time_stamp_ordering(file_reader, channel=channel)

    logger.info(f"Tests passed: {passed}")
