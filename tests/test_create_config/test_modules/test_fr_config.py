from unittest.mock import patch

from pyxspress.create_config.modules.fr_config import (
    create_fr_config_file,
    create_fr_launch_script,
)


@patch("os.chmod")
def test_create_fr_launc_script(mock_chmod, tmp_path, template_dir) -> None:
    # Setup
    num_cards = 2

    target_dir = tmp_path

    # Call function
    create_fr_launch_script(num_cards, template_dir, target_dir)

    # Assert
    for card in range(num_cards):
        assert (target_dir / f"stFrameReceiver{card + 1}.sh").exists()
        text = (target_dir / f"stFrameReceiver{card + 1}.sh").read_text()
        num = f"{(10 * card):03d}"
        assert (
            "/odin/prefix/bin/frameReceiver --io-threads 1 "
            f"--ctrl=tcp://0.0.0.0:10{num} "
            f"--config=$SCRIPT_DIR/fr{card + 1}.json "
            f"--log-config $SCRIPT_DIR/log4cxx.xml" in text
        )

    assert mock_chmod.call_count == num_cards


def test_create_fr_config_file(tmp_path, template_dir) -> None:
    # Setup
    num_cards = 2
    target_dir = tmp_path

    # call function
    create_fr_config_file(num_cards, template_dir, target_dir)

    for card in range(num_cards):
        assert (target_dir / f"fr{card + 1}.json").exists()
        text = (target_dir / f"fr{card + 1}.json").read_text()
        assert "{}" not in text  # no placeholders left
        release = f"{(10 * card + 2):03d}"
        assert f'"frame_release_endpoint": "tcp://127.0.0.1:10{release}"' in text
