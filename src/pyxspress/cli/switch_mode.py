import argparse
import logging

from pyxspress.switch_mode.processes_stop import processes_stop
from pyxspress.switch_mode.start_new_mode import start_new_mode


def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s][%(levelname)7s][%(filename)8s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    return logger


def main() -> None:
    parser = argparse.ArgumentParser(
        description=
        "Switch between EPICS, ODIN and Autocalib processes."
    )
    parser.add_argument(
        "-nc", "--no-confirm", action="store_false", help=
        "Skip user confirmation before killing processes"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    parser.add_argument(
        "-s",
        "--start",
        choices=("a", "o", "e"),
        help="Start process 'a' (autocalib), 'o' (ODIN), or 'e' (EPICS)",
    )

    args = parser.parse_args()
    logger = setup_logging(args.verbose)

    confirm = args.no_confirm

    start_mode = args.start

    if not processes_stop(confirm):
        logger.error("Processes not stopped, try running again")
        return

    if start_mode is not None:

        match start_mode:
            case "a":
                mode = "autocalib"
            case "o":
                mode = "odin"
            case "e":
                mode = "epics"

            case _:
                logger.error("Wrong mode entered")
        logger.info(f"Starting Process {mode}")
        result = start_new_mode(mode)
        started_msg = f"Mode {mode} "
        started_msg += "started sucessfully" if result == 0 else "could not start"
        logger.info(started_msg)


if __name__ == "__main__":
    main()
