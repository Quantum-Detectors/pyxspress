import os
import string
from pathlib import Path


def frame_processor(num_cards: int, template_dir: Path, target_dir: Path):
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


def frame_processor_json(num_cards: int, template_dir: Path, target_dir: Path):
    """Create the frame processor configuration file

    Args:
        num_cards (int): Number of cards
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """

    with open(template_dir / "fp.json.template") as fp_js_t:
        template_string = fp_js_t.read()

    # TODO: what is this?
    letter = list(string.ascii_uppercase)

    for card in range(num_cards):
        frame_processor_json_str = template_string.replace(
            "{ready}", f"{(10 * card) + 1:03d}"
        )
        frame_processor_json_str = frame_processor_json_str.replace(
            "{release}", f"{(10 * card) + 2:03d}"
        )
        frame_processor_json_str = frame_processor_json_str.replace(
            "{meta}", f"{(10 * card) + 8:03d}"
        )
        frame_processor_json_str = frame_processor_json_str.replace(
            "{lv_socket}", f"{card:02d}"
        )
        frame_processor_json_str = frame_processor_json_str.replace(
            "{list_channels}", f"[{card * 2}, {(card * 2) + 1}]"
        )
        frame_processor_json_str = frame_processor_json_str.replace(
            "{postfix}", f"_{letter[card]}"
        )
        frame_processor_json_str = frame_processor_json_str.replace(
            "{chan_1}", f"{card * 2}"
        )
        frame_processor_json_str = frame_processor_json_str.replace(
            "{chan_2}", f"{(card * 2) + 1}"
        )

        target_filepath = target_dir / f"fp{card + 1}.json"
        with open(target_filepath, "w") as fp_json_file:
            fp_json_file.write(frame_processor_json_str)
