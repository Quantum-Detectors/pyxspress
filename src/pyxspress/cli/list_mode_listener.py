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
@click.option(
    "-tr",
    "--tcp_relay",
    is_flag=True,
    default=False,
    help="Listen via TCP relay server instead of direct Xspress connection",
)
def main(num_cards: int, file_prefix: str | None, tcp_relay: bool):
    logger = setup_basic_logging()

    if tcp_relay:
        ip_addresses = ["127.0.0.1" for card_ip in range(2, 2 + num_cards)]
        ports = [13001 + card_num for card_num in range(num_cards)]
    else:
        ip_addresses = [f"192.168.0.{card_ip}" for card_ip in range(2, 2 + num_cards)]
        ports = [30125 for _ in range(num_cards)]

    file_names: list[str | None]
    if file_prefix:
        file_names = [
            f"{file_prefix}-card_{card}.bin" for card in range(1, num_cards + 1)
        ]
    else:
        file_names = [None for _ in range(num_cards)]

    process_list: list[Popen] = []
    for ip_address, port, filename in zip(
        ip_addresses, ports, file_names, strict=False
    ):
        command = [
            sys.executable,
            "-m",
            "pyxspress.list_mode.run_listener",
            ip_address,
            str(port),
        ]
        if filename is not None:
            command.append(filename)

        process_list.append(Popen(command, stdin=PIPE, stdout=PIPE))

    input("Press Enter to stop all listeners\n> ")
    for process in process_list:
        process.communicate(b"quitting\n")

    logger.info("Exiting...")
