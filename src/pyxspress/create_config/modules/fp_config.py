import json
import os
import string
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def create_fp_launch_script(
    num_cards: int, template_dir: Path, target_dir: Path
) -> None:
    """Create the frame processor launch script

    Args:
        num_cards (int): Number of cards
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """

    with open(template_dir / "stFrameProcessor.template") as fp_t:
        template_string = fp_t.read()

    for card in range(num_cards):
        frame_processor_str = template_string.replace("{card}", str(card + 1))
        frame_processor_str = frame_processor_str.replace(
            "{num}", f"{(10 * card) + 4:03d}"
        )

        target_filepath = target_dir / f"stFrameProcessor{card + 1}.sh"
        with open(target_filepath, "w") as fp_file:
            fp_file.write(frame_processor_str)

        # Make executable
        os.chmod(target_filepath, 0o755)


def _get_mca_datasets(
    first_channel: int, last_channel: int
) -> dict[str, dict[str, dict[str, dict]]]:
    datasets: dict[str, dict[str, dict[str, dict]]] = {"hdf": {"dataset": {}}}
    for channel in range(first_channel, last_channel + 1):
        datasets["hdf"]["dataset"][f"mca_{channel}"] = {
            "datatype": "uint32",
            "chunks": [256, 1, 4096],
            "dims": [1, 4096],
            "compression": "blosc",
            "indexes": True,
        }

    return datasets


def _get_list_mode_datasets(
    first_channel: int, last_channel: int, num_events_per_chunk: int
) -> dict[str, dict[str, dict[str, dict]]]:
    datasets: dict[str, dict[str, dict[str, dict]]] = {"hdf": {"dataset": {}}}
    for channel in range(first_channel, last_channel + 1):
        # Time frame
        datasets["hdf"]["dataset"][f"ch{channel}_time_frame"] = {
            "datatype": "uint64",
            "chunks": [num_events_per_chunk],
        }
        # Time stamp
        datasets["hdf"]["dataset"][f"ch{channel}_time_stamp"] = {
            "datatype": "uint64",
            "chunks": [num_events_per_chunk],
        }
        # Event height
        datasets["hdf"]["dataset"][f"ch{channel}_event_height"] = {
            "datatype": "uint16",
            "chunks": [num_events_per_chunk],
        }
        # Reset flag
        datasets["hdf"]["dataset"][f"ch{channel}_reset_flag"] = {
            "datatype": "uint8",
            "chunks": [num_events_per_chunk],
        }

    return datasets


def create_fp_config_file(num_cards: int, template_dir: Path, target_dir: Path) -> None:
    """Create the frame processor JSON configuration file

    Args:
        num_cards (int): Number of cards
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """
    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template("fp.json.template")

    # List of all letters to map from card index to alphabet
    letter = list(string.ascii_uppercase)

    base_port = 10000

    for card_num in range(num_cards):
        card_offset = 10 * card_num
        start_chan = card_num * 2
        end_chan = card_num * 2 + 1

        ready_port = base_port + 1 + card_offset
        release_port = base_port + 2 + card_offset
        meta_port = base_port + 8 + card_offset

        live_view_port = 15500 + card_num

        filename_postfix = f"_{letter[card_num]}"

        channel_list: list[int] = list(range(start_chan, end_chan + 1))

        mca_datasets = json.dumps(_get_mca_datasets(start_chan, end_chan))
        master_mca_dataset = f"mca_{card_num * 2 + 1}"

        # Number of events that get built into a single frame by the list
        # mode plugin. This will need to match the HDF chunk size otherwise
        # we end up with missing data in the HDF file.
        num_events_per_frame = 524280

        list_mode_datasets = json.dumps(
            _get_list_mode_datasets(start_chan, end_chan, num_events_per_frame)
        )

        fp_json_config = template.render(
            meta_port=meta_port,
            ready_port=ready_port,
            release_port=release_port,
            live_view_port=live_view_port,
            filename_postfix=filename_postfix,
            mca_datasets=mca_datasets,
            master_mca_dataset=master_mca_dataset,
            channel_list=channel_list,
            list_mode_datasets=list_mode_datasets,
            num_events_per_frame=num_events_per_frame,
        )

        # Parse as a JSON dict and format it nicely before saving
        formatted_config = json.dumps(json.loads(fp_json_config), indent=4)

        target_filepath = target_dir / f"fp{card_num + 1}.json"
        with open(target_filepath, "w") as fp_json_file:
            fp_json_file.write(formatted_config + "\n")
