from unittest.mock import patch

from pyxspress.create_config.modules.fp_config import (
    create_fp_config_file,
    create_fp_launch_script,
    get_master_list_mode_dataset,
)

from .util import get_8ch_file_string


@patch("os.chmod")
def test_create_fp_launch_script(mock_chmod, tmp_path, template_dir) -> None:
    # Setup
    num_cards = 2
    target_dir = tmp_path

    # Call function
    create_fp_launch_script(num_cards, template_dir, target_dir)

    # Assert
    for card in range(num_cards):
        assert (target_dir / f"stFrameProcessor{card + 1}.sh").exists()
        text = (target_dir / f"stFrameProcessor{card + 1}.sh").read_text()
        num = f"{(10 * card) + 4:03d}"
        assert (
            f"/odin/prefix/bin/frameProcessor --ctrl=tcp://0.0.0.0:10{num} "
            f"--config=$SCRIPT_DIR/fp{card + 1}.json "
            f"--log-config $SCRIPT_DIR/log4cxx.xml" in text
        )

    assert mock_chmod.call_count == num_cards


def test_create_fp_config_file(tmp_path, template_dir) -> None:
    # Setup
    num_cards = 4
    marker_channels = False
    target_dir = tmp_path

    create_fp_config_file(num_cards, template_dir, target_dir, marker_channels)

    for card in range(num_cards):
        # Check that we generated 1 processor config per card
        assert (target_dir / f"fp{card + 1}.json").exists()
        text = (target_dir / f"fp{card + 1}.json").read_text()

        # Check no substitutions remain
        assert "{{" not in text
        assert "}}" not in text

        # Compare to our example test files
        expected_contents = get_8ch_file_string(f"fp{card + 1}.json")
        assert text == expected_contents


def test_get_master_list_mode_dataset_first_card() -> None:
    card_num = 0

    expected_dataset = "ch1_reset_flag"

    assert get_master_list_mode_dataset(card_num) == expected_dataset


def test_get_master_list_mode_dataset_second_card() -> None:
    card_num = 1

    expected_dataset = "ch3_reset_flag"

    assert get_master_list_mode_dataset(card_num) == expected_dataset
