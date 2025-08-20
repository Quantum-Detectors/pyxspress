"""
Data GUI module

Creates a basic GUI for reading the Xspress Odin HDF5 files.

"""

import logging
import sys

import click
from PySide6.QtWidgets import QApplication

from pyxspress.gui.main_window import MainWindow
from pyxspress.util.util import setup_basic_logging


@click.command(
    help="Browse Xspress Odin data using a basic GUI",
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]},
)
@click.option("-d", "--debug", is_flag=True, default=False, help="Enable debug logging")
def main(debug: bool):
    """Run the GUI application

    Args:
        debug (bool): Enable debug logging
    """
    # Logging
    log_level = logging.DEBUG if debug else logging.INFO
    logger = setup_basic_logging(log_level=log_level)

    logger.debug("Launching GUI")
    q_app = QApplication([])

    # Keep a reference to avoid being garbage collected
    _ = MainWindow()

    exit_code = q_app.exec()

    logger.debug(f"Exiting with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
