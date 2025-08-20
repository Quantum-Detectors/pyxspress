"""
Create the Odin Xspress runtime configuration

This is used to generate all of the files needed to run Odin based on the
connected Xspress system.

This includes:

- Odin server configuration files
- Launch scripts for Odin and EPICS processes

"""

import math
import os
from pathlib import Path

import click

from pyxspress import get_module_version_string
from pyxspress.create_config.config_generator import ConfigGenerator
from pyxspress.util import setup_basic_logging


@click.command(
    help="Generate the Odin runtime configuration for an Xspress system",
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]},
)
@click.option(
    "-c",
    "--channels",
    type=int,
    default=8,
    help="Number of channels in the system",
)
@click.option(
    "-m",
    "--mark",
    type=int,
    default=2,
    help="Generation of Xspress 3X system (Mk1 or Mk2)",
)
@click.option(
    "-od",
    "--odin_dir",
    type=str,
    default="/odin/config",
    help="Where to write generated Odin configuration files",
)
@click.option(
    "-ed",
    "--epics_dir",
    type=str,
    default="/odin/epics/config",
    help="Where to write generated EPICS configuration files",
)
@click.option(
    "-t",
    "--test",
    is_flag=True,
    default=False,
    help="Used for developer testing (creates files in place)",
)
@click.option(
    "-v",
    "--version",
    is_flag=True,
    default=False,
    help="Print version and exit",
)
def main(
    channels: int, mark: int, odin_dir: str, epics_dir: str, test: bool, version: bool
) -> None:
    if version:
        print(get_module_version_string())
        return

    logger = setup_basic_logging()

    if test:
        # Change output directories
        odin_dir = f"{os.getcwd()}/config"
        epics_dir = f"{os.getcwd()}/config"

    if mark == 1:
        raise ValueError("Mark 1 not currently supported")

    logger.info(f"Odin output directory: {odin_dir}")
    logger.info(f"EPICS config directory: {epics_dir}")

    odin_path = Path(odin_dir)
    epics_path = Path(epics_dir)

    # Validate the paths aren't files
    if odin_path.is_file():
        raise ValueError(f"Odin config directory path {odin_path} is a file!")
    if epics_path.is_file():
        raise ValueError(f"EPICS config directory path {epics_path} is a file!")

    # Sanity check the Odin configuration path ends in config, as this will
    # be deleted by our ConfigGenerator.
    if odin_path.name != "config":
        user_input = ""
        while True:
            user_input = input(
                "  WARNING: Odin config path does not end in 'config'.\n"
                "           This directory will be cleaned before new \n"
                "           configuration is generated.\n"
                "  Proceed? (Y/N)\n > "
            )
            if user_input.upper() == "N":
                print("Operation aborted. Exiting.")
                return
            elif user_input.upper() == "Y":
                break

    # Generate configuration
    generator = ConfigGenerator(
        num_cards=math.ceil(int(channels) / 2),
        num_chans=channels,
        mark=mark,
        odin_path=odin_path,
        epics_path=epics_path,
        test=test,
    )
    generator.clean()
    generator.generate()


if __name__ == "__main__":
    main()
