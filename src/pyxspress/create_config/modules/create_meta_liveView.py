import os
from pathlib import Path


def _meta_writer_sensor(num_chans):
    return f"--sensor-shape {num_chans} 4096"


def _meta_writer_endpoints(num_cards):
    ep_str = ""
    for card in range(num_cards):
        ep_str += f"tcp://127.0.0.1:10{8 + (10 * card):03d},"
    return ep_str.strip(",")


def _live_view(num_cards):
    live_view_str = ""
    for card in range(num_cards):
        live_view_str += f"155{card:02d},"
    return live_view_str.strip(",")


def live_view_file(num_cards: int, template_dir: Path, target_dir: Path):
    """Create the live view config file

    Args:
        num_cards (int): Number of cards
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """
    with open(template_dir / "stLiveViewMerge.sh.template") as live_view_temp:
        live_view_string = live_view_temp.read()

    ports = _live_view(num_cards)
    live_view_string = live_view_string.replace("{ports}", ports)

    target_filepath = target_dir / "stLiveViewMerge.sh"
    with open(target_filepath, "w") as live_view_file:
        live_view_file.write(live_view_string)

    # Make executable
    os.chmod(target_filepath, 0o755)


def meta_writer_file(
    num_cards: int, num_chans: int, template_dir: Path, target_dir: Path
) -> None:
    """Create the metawriter config file

    Args:
        num_cards (int): Number of cards in Xspress system
        num_chans (int): Number of channels in Xspress system
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """
    meta_endpoints = _meta_writer_endpoints(num_cards)
    sensor_shape = _meta_writer_sensor(num_chans)

    with open(template_dir / "stMetaWriter.sh.template") as meta_writer_temp:
        meta_writer_string = meta_writer_temp.read()

    meta_writer_string = meta_writer_string.replace("{meta_endpoints}", meta_endpoints)
    meta_writer_string = meta_writer_string.replace("{sensor_shape}", sensor_shape)

    target_filepath = target_dir / "stMetaWriter.sh"
    with open(target_filepath, "w") as meta_writer_file:
        meta_writer_file.write(meta_writer_string)

    # Make executable
    os.chmod(target_filepath, 0o755)
