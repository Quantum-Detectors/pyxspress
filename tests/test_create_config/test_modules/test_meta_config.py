from unittest.mock import patch

from pyxspress.create_config.modules.meta_config import (
    _live_view,
    _meta_writer_endpoints,
    _meta_writer_sensor,
    create_live_view_launch_script,
    create_meta_writer_launch_script,
)


def test_meta_writer_sensor() -> None:
    num_chans = 4
    sensor = _meta_writer_sensor(num_chans)
    expected = f"--sensor-shape {num_chans} 4096"
    assert sensor == expected


def test_meta_writer_endpoints() -> None:
    num_cards = 4
    endpoints = _meta_writer_endpoints(num_cards)
    for card in range(num_cards):
        # Check without the trailing comma
        ep_str = f"tcp://127.0.0.1:10{8 + (10 * card):03d}"
        assert ep_str in endpoints


def test_live_view() -> None:
    num_cards = 4
    live_view = _live_view(num_cards)
    for card in range(num_cards):
        # Check without the trailing comma
        live_view_str = f"155{card:02d}"
        assert live_view_str in live_view


@patch("pyxspress.create_config.modules.meta_config._live_view")
@patch("os.chmod")
def test_live_view_file(mock_chmod, mock_live_view, template_dir, tmp_path) -> None:
    num_cards = 2
    mock_live_view.return_value = "15500,15501"
    create_live_view_launch_script(num_cards, template_dir, tmp_path)
    assert mock_live_view.called
    assert (tmp_path / "stLiveViewMerge.sh").exists()
    text = (tmp_path / "stLiveViewMerge.sh").read_text()
    assert "{}" not in text
    assert "15500,15501" in text
    assert mock_chmod.called


@patch("pyxspress.create_config.modules.meta_config._meta_writer_endpoints")
@patch("pyxspress.create_config.modules.meta_config._meta_writer_sensor")
@patch("os.chmod")
def test_meta_writer_file(
    mock_chmod,
    mock_meta_writer_sensor,
    mock_meta_writer_endpoints,
    template_dir,
    tmp_path,
) -> None:
    num_cards = 2
    num_chans = 4

    mock_meta_writer_sensor.return_value = "sensor response"
    mock_meta_writer_endpoints.return_value = "endpoints response"

    create_meta_writer_launch_script(num_cards, num_chans, template_dir, tmp_path)
    assert mock_meta_writer_sensor.called
    assert mock_meta_writer_endpoints.called
    assert (tmp_path / "stMetaWriter.sh").exists()
    text = (tmp_path / "stMetaWriter.sh").read_text()
    assert "sensor response" in text
    assert "endpoints response" in text
    assert mock_chmod.called
