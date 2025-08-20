"""
Xspress Mini Mk2 list mode test script

Used to test listening to the TCP sockets used to send list mode
event data from each ADC card.
"""

import sys
from subprocess import PIPE, Popen

import click

from pyxspress.util.util import setup_basic_logging


@click.command(
    help="Start up listeners to listen to the list mode event streams for each card.",
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]},
)
@click.option("-n", "--num_cards", type=int, default=1, help="Number of ADC cards")
@click.option(
    "-f",
    "--file_prefix",
    type=str,
    default=None,
    help="Filename prefix for saving data",
)
def main(num_cards: int, file_prefix: str | None):
    logger = setup_basic_logging()

    ip_addresses = [f"192.168.0.{card_ip}" for card_ip in range(2, 2 + num_cards)]
    file_names: list[str | None]
    if file_prefix:
        file_names = [
            f"{file_prefix}-card_{card}.bin" for card in range(1, num_cards + 1)
        ]
    else:
        file_names = [None for _ in range(num_cards)]

    process_list: list[Popen] = []
    for ip_address, filename in zip(ip_addresses, file_names, strict=False):
        command = [sys.executable, "-m", "pyxspress.list_mode.run_listener", ip_address]
        if filename is not None:
            command.append(filename)

        process_list.append(Popen(command, stdin=PIPE, stdout=PIPE))

    input("Press Enter to stop all listeners\n> ")
    for process in process_list:
        process.communicate(b"quitting\n")

    logger.info("Exiting...")
