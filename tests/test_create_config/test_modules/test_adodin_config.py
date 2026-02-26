from subprocess import CalledProcessError
from unittest.mock import patch

from pyxspress.create_config.modules.adodin_config import (
    _odin_data_template,
    _odin_procserv_template,
    _xspress_channel_template,
    _xspress_fem_template,
    generate_ioc_db_substitutions,
    rebuild_adodin,
)

from .util import get_8ch_Mk2_file_string


def test_odin_data_template() -> None:
    result = _odin_data_template(2)
    expected = (
        '    { "XSPRESS", ":OD1:", "ODN.OD", "1", "0", "2" }\n'
        '    { "XSPRESS", ":OD2:", "ODN.OD", "1", "1", "2" }'
    )
    assert result == expected


def test_xspress_channel_template() -> None:
    result = _xspress_channel_template(2)
    expected = (
        '    { "XSPRESS", ":CAM:", "ODN.CAM", "0", "1", "2", "1" }\n'
        '    { "XSPRESS", ":CAM:", "ODN.CAM", "1", "2", "2", "1" }'
    )
    assert result == expected


def test_xspress_fem_template() -> None:
    result = _xspress_fem_template(2)
    expected = (
        '    { "XSPRESS", ":CAM:", "ODN.CAM", "0", "2", "1" }\n'
        '    { "XSPRESS", ":CAM:", "ODN.CAM", "1", "2", "1" }'
    )
    assert result == expected


def test_odin_procserv_template() -> None:
    result = _odin_procserv_template(3)
    assert "FrameReceiver3" in result
    assert "FrameProcessor3" in result
    assert result.startswith('    { "ODN", "OdinServer"')


@patch("pyxspress.create_config.modules.adodin_config.shutil.copy")
def test_generate_ioc_db_substitutions_succeeds_and_does_not_copy_with_test_mode(
    mock_shutil_copy, tmp_path, template_dir
) -> None:
    # Generate for 8 channels so we can compare to our example test file
    num_cards = 4
    num_chans = 8
    adodin_db_dir = tmp_path
    epics_config_dir = tmp_path
    test = True

    # Call function in test mode
    generate_ioc_db_substitutions(
        num_cards, num_chans, template_dir, adodin_db_dir, epics_config_dir, test
    )

    # Read the generated file
    output_file = tmp_path / "xspress_expanded.substitutions"
    generated_contents = output_file.read_text()

    expected_contents = get_8ch_Mk2_file_string("xspress_expanded.substitutions")
    assert generated_contents == expected_contents

    # Check the mocked shutil copy was never called
    mock_shutil_copy.assert_not_called()


@patch("pyxspress.create_config.modules.adodin_config.shutil.copy")
def test_generate_ioc_db_substitutions_succeeds_does_copy_with_normal_mode(
    mock_shutil_copy, tmp_path, template_dir
) -> None:
    # Generate for 8 channels so we can compare to our example test file
    num_cards = 4
    num_chans = 8
    adodin_db_dir = tmp_path
    epics_config_dir = tmp_path
    test = False

    # Call function in test mode
    generate_ioc_db_substitutions(
        num_cards, num_chans, template_dir, adodin_db_dir, epics_config_dir, test
    )

    # Read the generated file
    output_file = tmp_path / "xspress_expanded.substitutions"
    generated_contents = output_file.read_text()

    expected_contents = get_8ch_Mk2_file_string("xspress_expanded.substitutions")
    assert generated_contents == expected_contents

    # Check the mocked shutil copy was never called
    mock_shutil_copy.assert_called_once()


@patch("pyxspress.create_config.modules.adodin_config.subprocess.run")
def test_rebuild_adodin_succeeds(mock_run, tmp_path) -> None:
    rebuild_adodin(tmp_path)

    mock_run.assert_called_once_with(["make"], cwd=tmp_path, check=True)


@patch("pyxspress.create_config.modules.adodin_config.subprocess.run")
def test_rebuild_adodin_does_not_raise_for_process_error(mock_run, tmp_path) -> None:
    # Make our mock run raise the exception we catch
    mock_run.side_effect = CalledProcessError(-1, "make")

    rebuild_adodin(tmp_path)

    mock_run.assert_called_once_with(["make"], cwd=tmp_path, check=True)
