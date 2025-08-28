import os
from pathlib import Path


def frame_receiver(num_cards: int, template_dir: Path, target_dir: Path):
    """Create the frame receiver launch script

    Args:
        num_cards (int): Number of cards
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """

    with open(template_dir / "stFrameReceiver.template") as fr_t:
        template_string = fr_t.read()

        for card in range(num_cards):
            frame_receiver = template_string.replace("{card}", f"{(card + 1)}")
            frame_receiver = frame_receiver.replace("{num}", f"{(10 * card):03d}")

            target_filepath = target_dir / f"stFrameReceiver{card + 1}.sh"
            with open(target_filepath, "w") as fr_file:
                fr_file.write(frame_receiver)

            # Make executable
            os.chmod(target_filepath, 0o755)


def frame_receiver_json(num_cards: int, template_dir: Path, target_dir: Path):
    """Create the frame receiver configuration file

    Args:
        num_cards (int): Number of cards
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """
    with open(template_dir / "fr.json.template") as fr_js_t:
        template_string = fr_js_t.read()

        for card in range(num_cards):
            frame_receiver = template_string.replace("{port}", f"{(card + 50)}")
            frame_receiver = frame_receiver.replace("{buf}", f"{(card + 1)}")
            frame_receiver = frame_receiver.replace("{ready}", f"{(10 * card + 1):03d}")
            frame_receiver = frame_receiver.replace(
                "{release}", f"{(10 * card + 2):03d}"
            )
            with open(target_dir / f"fr{card + 1}.json", "w") as fr_json_file:
                fr_json_file.write(frame_receiver)
