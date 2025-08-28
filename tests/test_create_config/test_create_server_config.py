from unittest.mock import patch

from pyxspress.create_config.modules.create_server_config import (
    _daq_endpoints,
    _processor_endpoints,
    _receiver_endpoints,
    odin_server_config,
)


def test_daq_endpoints():
    num_cards = 3
    result = _daq_endpoints(num_cards)
    for card in range(num_cards):
        daq_ep_str = f"tcp://127.0.0.1:151{50 + card}"
        assert daq_ep_str in result


def test_processor_endpoints():
    num_cards = 3
    result = _processor_endpoints(num_cards)
    for card in range(num_cards):
        fp_ep_str = f"127.0.0.1:10{4 + (10 * card):03d}"
        assert fp_ep_str in result


def test_receiver_endpoints():
    num_cards = 3
    result = _receiver_endpoints(num_cards)
    for card in range(num_cards):
        fr_ep_str = f"127.0.0.1:10{(10 * card):03d}"
        assert fr_ep_str in result


@patch("pyxspress.create_config.modules.create_server_config._processor_endpoints")
@patch("pyxspress.create_config.modules.create_server_config._receiver_endpoints")
@patch("pyxspress.create_config.modules.create_server_config._daq_endpoints")
def test_odin_server_config(
    mock_daq, mock_receiver, mock_processor, template_dir, tmp_path
):
    num_cards = 3
    num_chans = 6
    mock_daq.return_value = "daq_endpoints"
    mock_receiver.return_value = "receiver_endpoints"
    mock_processor.return_value = "processor_endpoints"

    odin_server_config(num_cards, num_chans, template_dir, tmp_path)

    assert (tmp_path / "odin_server.cfg").exists()
    text = (tmp_path / "odin_server.cfg").read_text()
    assert "daq_endpoints" in text
    assert "receiver_endpoints" in text
    assert "processor_endpoints" in text
    assert "{}" not in text
