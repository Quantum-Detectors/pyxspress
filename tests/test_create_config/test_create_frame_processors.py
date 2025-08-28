from unittest.mock import patch

from pyxspress.create_config.modules.create_frame_processors import (
    frame_processor,
    frame_processor_json,
)


@patch("os.chmod")
def test_frame_processor(mock_chmod, tmp_path, template_dir):
    # Setup
    num_cards = 2
    target_dir = tmp_path

    # Call function
    frame_processor(num_cards, template_dir, target_dir)

    # Assert
    for card in range(num_cards):
        assert (target_dir / f"stFrameProcessor{card + 1}.sh").exists()
        text = (target_dir / f"stFrameProcessor{card + 1}.sh").read_text()
        num = f"{(10 * card) + 4:03d}"
        assert (
            f"/odin/prefix/bin/frameProcessor --ctrl=tcp://0.0.0.0:10{num} "
            f"--config=$SCRIPT_DIR/fp{card + 1}.json "
            f"--log-config $SCRIPT_DIR/log4cxx.xml"
            in text
        )

    assert mock_chmod.call_count == num_cards


def test_frame_processor_json(tmp_path, template_dir):
    # Setup
    num_cards = 2
    target_dir = tmp_path

    # call function
    frame_processor_json(num_cards, template_dir, target_dir)

    for card in range(num_cards):
        assert (target_dir / f"fp{card + 1}.json").exists()
        text = (target_dir / f"fp{card + 1}.json").read_text()
        assert "{}" not in text  # no placeholders left
        num = f"{(10 * card) + 2:03d}"
        assert f'"fr_release_cnxn": "tcp://127.0.0.1:10{num}"' in text
        list_channels = f"[{card * 2}, {(card * 2) + 1}]"
        assert f'"channels": {list_channels},' in text
