import os
from unittest.mock import patch

from click.testing import CliRunner

from pyxspress.cli.create_config import main


def test_cli_version_runs_successfully():
    runner = CliRunner()
    result = runner.invoke(main, args=["-v"])
    assert result.exit_code == 0


@patch("pyxspress.cli.create_config.os.getcwd")
def test_cli_creates_local_config(mock_os_getcwd, tmp_path):
    mock_os_getcwd.return_value = str(tmp_path)

    assert not os.path.exists(tmp_path / "config")

    runner = CliRunner()
    result = runner.invoke(main, args=["-t"])
    assert result.exit_code == 0

    assert os.path.exists(tmp_path / "config")
