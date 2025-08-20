"""
Xspress data plotting script

A very basic script used to read decompressed Xspress HDF5 files
and plots the data from a channel dataset.

Use within a environment with the requirements listed in requirements.txt
installed.

.. note::
    Make sure that the Diamond HDF5 filters are on the PATH (this
    is already in the .bashrc_odin profile if that is loaded) in order to
    read compressed data in files:

    - `export HDF5_PLUGIN_PATH=/odin/prefix/h5plugin`

    Otherwise on the source server decompress first:

    - `h5repack -f data:NONE compressed.h5 bloated.h5`

"""

import sys

import click
import h5py
import numpy
from matplotlib import pyplot


@click.command(
    help="Plot the dataset for an Xspress channel",
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
@click.argument("filename", required=True, type=str)
@click.argument("channel", required=True, type=int, default=0)
@click.option(
    "-af",
    "--all_frames",
    is_flag=True,
    default=False,
    help="Print all frames",
)
def main(filename: str, channel: int, all_frames: bool = False):
    """Plot the data for a single channel of the Xspress system

    Args:
        filename (str): Filename of decompressed dataset
        channel (int): Xspress channel
        all_frames (bool, optional): If True, plot all frames within dataset.
                                     Otherwise just plot the first frame.
                                     Defaults to False.
    """
    dataset = f"mca_{channel}"
    print(f"Reading dataset {dataset} from {filename}")
    with h5py.File(filename) as input_file:
        datasets = list(input_file)
        print(f"Available datasets: {datasets}")
        if dataset not in datasets:
            raise ValueError(
                f"Dataset '{dataset}' not found for channel {channel}. "
                "Did you pick a valid channel for the file?"
            )

        data: numpy.ndarray = input_file[dataset][:]

    print(f"Got data of shape: {data.shape}")

    if all_frames:
        print("Plotting all frames")
        for i in range(data.shape[0]):
            pyplot.plot(data[i, 0, :])
            print(f"Frame {i} index of maximum: {numpy.argmax(data[i])}")
    else:
        print("Plotting first frame only")
        pyplot.plot(data[0, 0, :])
        print(f"Index of maximum: {numpy.argmax(data[0, 0, :])}")

    pyplot.title(f"{filename} - channel {channel}")
    pyplot.xlabel("Bin")
    pyplot.ylabel("Counts")

    pyplot.show()


def get_user_args() -> list[str]:
    """Get the list of system arguments passed without the first argument

    Returns:
        list: List of system arguments
    """
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    else:
        args = []
    return args


if __name__ == "__main__":
    main(args=get_user_args())
