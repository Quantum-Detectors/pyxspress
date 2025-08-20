"""
Run listener

Module used to run a single ListModeListener

Used by the listener CLI to be able to run each listener as a separate process
to avoid the limitation of the GIL and reduce performance.
"""

import sys

from pyxspress.list_mode import ListModeListener
from pyxspress.util import setup_basic_logging


def run_single_listener(ip_address: str, file_path: str | None):
    """Start a single event mode listener to listen to a single ADC card

    Args:
        ip_address (str): IP address of ADC card
        file_path (Optional[str]): File path to write binary data to
    """
    logger = setup_basic_logging()
    logger.info(f"Running listener for card {ip_address} to save to {file_path}")

    listener = ListModeListener(ip_address, file_name=file_path)

    # Wait for input to quit
    input()

    logger.info(f"Stopping listener for {ip_address}")
    listener.stop()

    logger.info(f"Listener stopped for {ip_address}")


if __name__ == "__main__":
    assert len(sys.argv) in [2, 3], (
        "Expected 1 or 2 additional arguments as 'ip_address file_path'. "
        f"Got {len(sys.argv) - 1} ({sys.argv})"
    )
    ip_address = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) == 3 else None
    run_single_listener(ip_address, file_path)
