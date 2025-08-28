from unittest.mock import patch

from pyxspress.create_config.modules.create_expanded_substitutions import (
    _odin_data_template,
    _odin_procserv_template,
    _xspress_channel_template,
    _xspress_fem_template,
    xspress_expanded_substitutions,
)


def test_odin_data_template():
    result = _odin_data_template(2)
    expected = (
        '    { "XSPRESS", ":OD1:", "ODN.OD", "1", "0", "2" }\n'
        '    { "XSPRESS", ":OD2:", "ODN.OD", "1", "1", "2" }'
    )
    assert result == expected


def test_xspress_channel_template():
    result = _xspress_channel_template(2)
    expected = (
        '    { "XSPRESS", ":CAM:", "ODN.CAM", "0", "1", "2", "1" }\n'
        '    { "XSPRESS", ":CAM:", "ODN.CAM", "1", "2", "2", "1" }'
    )
    assert result == expected


def test_xspress_fem_template():
    result = _xspress_fem_template(2)
    expected = (
        '    { "XSPRESS", ":CAM:", "ODN.CAM", "0", "2", "1" }\n'
        '    { "XSPRESS", ":CAM:", "ODN.CAM", "1", "2", "1" }'
    )
    assert result == expected


def test_odin_procserv_template():
    result = _odin_procserv_template(3)
    assert "FrameReceiver3" in result
    assert "FrameProcessor3" in result
    assert result.startswith('    { "ODN", "OdinServer"')


def test_xspress_expanded_substitutions_writes_file(tmp_path):
    # Setup fake template file
    template_content = (
        "{chans} {cards}\n"
        "{odin_data_template}\n"
        "{xspress_channel_template}\n"
        "{xspress_fem_template}\n"
        "{odin_procserv_template}"
    )
    template_file = tmp_path / "xspress_expanded.substitutions.template"
    template_file.write_text(template_content)

    # Call function in test mode (no subprocess)
    xspress_expanded_substitutions(
        num_cards=1,
        num_chans=1,
        template_dir=tmp_path,
        adodin_dir=tmp_path,  # unused in test mode
        adodin_db_dir=tmp_path,
        epics_config_dir=tmp_path,
        test=True,
    )

    # Verify output file exists and has replaced text
    output_file = tmp_path / "xspress_expanded.substitutions"
    text = output_file.read_text()
    assert "1 1" in text
    assert "ODN.OD" in text  # came from odin_data_template
    assert "{}" not in text  # no placeholders left


@patch("subprocess.run")
@patch("shutil.copy")
def test_xspress_expanded_substitutions_runs_make(mock_copy, mock_run, tmp_path):
    # Prepare dirs + files
    template_file = tmp_path / "xspress_expanded.substitutions.template"
    template_file.write_text("{chans} {cards}")

    db_dir = tmp_path / "db"
    db_dir.mkdir()

    xspress_expanded_substitutions(
        num_cards=1,
        num_chans=1,
        template_dir=tmp_path,
        adodin_dir=tmp_path,
        adodin_db_dir=db_dir,
        epics_config_dir=tmp_path,
        test=False,
    )

    mock_copy.assert_called_once()
    mock_run.assert_called_once_with(["make"], cwd=tmp_path, check=True)
