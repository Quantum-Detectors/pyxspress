from unittest.mock import patch

from pyxspress.create_config.modules.odin_launcher import (
    _odin_processes,
    launch_n_chan,
)


def test_odin_processes() -> None:
    num_cards = 3
    result_string = _odin_processes(num_cards)

    base_port = 4010
    for i in range(num_cards):
        odin_process_string = (
            f"procServ -P {base_port + (i * 2)} "
            f"/odin/config/stFrameReceiver{i + 1}.sh\n"
        )
        odin_process_string += (
            f"procServ -P {base_port + (i * 2) + 1} "
            f"/odin/config/stFrameProcessor{i + 1}.sh\n"
        )
        assert odin_process_string in result_string
        assert "procServ -P 4004 /odin/config/stLiveViewMerge.sh\n\n" in result_string


@patch("pyxspress.create_config.modules.odin_launcher._odin_processes")
@patch("os.chmod")
def test_launch_n_chan_no_relay_server_substitutes_strings(
    mock_chmod, mock_odin_processes, template_dir, tmp_path
) -> None:
    num_cards = 2
    num_chans = 4
    mock_output_text = "mocked_odin_processes_output"
    mock_odin_processes.return_value = mock_output_text

    launch_n_chan(num_cards, num_chans, False, template_dir, tmp_path)

    assert mock_odin_processes.called_with(num_cards)
    assert (tmp_path / f"launch_{num_chans}chan_odin.sh").exists()
    text = (tmp_path / f"launch_{num_chans}chan_odin.sh").read_text()
    assert "{}" not in text
    assert mock_output_text in text
    assert mock_chmod.called


@patch("pyxspress.create_config.modules.odin_launcher._odin_processes")
@patch("os.chmod")
def test_launch_n_chan_with_relay_server_substitutes_strings(
    mock_chmod, mock_odin_processes, template_dir, tmp_path
) -> None:
    num_cards = 2
    num_chans = 4
    mock_output_text = "mocked_odin_processes_output"
    mock_odin_processes.return_value = mock_output_text

    launch_n_chan(num_cards, num_chans, True, template_dir, tmp_path)

    assert mock_odin_processes.called_with(num_cards)
    assert (tmp_path / f"launch_{num_chans}chan_odin.sh").exists()
    text = (tmp_path / f"launch_{num_chans}chan_odin.sh").read_text()
    assert "{}" not in text
    assert mock_output_text in text
    assert mock_chmod.called
