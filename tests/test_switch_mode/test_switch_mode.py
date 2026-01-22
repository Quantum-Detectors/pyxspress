import subprocess
from unittest.mock import MagicMock, patch

from pyxspress.switch_mode.processes_stop import (
    kill_process,
    kill_script,
    processes_stop,
    stop_all,
)


@patch("pyxspress.switch_mode.processes_stop.check_process_running")
def test_kill_process_already_stopped(mock_running):
    mock_running.return_value = False

    assert kill_process("1234") is True
    mock_running.assert_called_once_with("1234")


@patch("pyxspress.switch_mode.processes_stop.subprocess.run")
@patch("pyxspress.switch_mode.processes_stop.check_process_running")
def test_kill_process_soft_kill(mock_running, mock_run):
    # running → stopped
    mock_running.side_effect = [True, False]

    mock_run.return_value = subprocess.CompletedProcess(
        args=["kill", "1234"], returncode=0
    )

    assert kill_process("1234") is True

@patch("pyxspress.switch_mode.processes_stop.subprocess.run")
@patch("pyxspress.switch_mode.processes_stop.check_process_running")
def test_kill_process_force_kill(mock_running, mock_run):
    # running → still running → stopped
    mock_running.side_effect = [True, True, False]

    mock_run.return_value = subprocess.CompletedProcess(
        args=["kill", "-9", "1234"], returncode=0
    )

    assert kill_process("1234") is True


@patch("builtins.input", return_value="y")
@patch("pyxspress.switch_mode.processes_stop.kill_process")
@patch("pyxspress.switch_mode.processes_stop.check_process_running")
def test_stop_all_confirm_yes(mock_running, mock_kill, mock_input):
    mock_kill.return_value = True
    mock_running.return_value = False

    procs = ["1234 testproc", "5678 otherproc"]

    result = stop_all(procs, confirm=True)

    assert result is True
    assert mock_kill.call_count == 2

@patch("builtins.input", return_value="n")
@patch("pyxspress.switch_mode.processes_stop.kill_process")
def test_stop_all_confirm_no(mock_kill, mock_input):
    procs = ["1234 testproc"]

    result = stop_all(procs, confirm=True)

    assert result is True
    mock_kill.assert_not_called()

@patch("builtins.input", return_value="y")
@patch("pyxspress.switch_mode.processes_stop.subprocess.Popen")
def test_kill_script_success(mock_popen, mock_input):
    mock_process = MagicMock()
    mock_process.stdout = ["killed\n"]
    mock_process.wait.return_value = 0

    mock_popen.return_value = mock_process

    result = kill_script("odin", "/fake", "kill.sh", confirm=True)

    assert result is True

@patch("pyxspress.switch_mode.processes_stop.process_list")
@patch("pyxspress.switch_mode.processes_stop.get_stop_script")
@patch("pyxspress.switch_mode.processes_stop.kill_script")
@patch("pyxspress.switch_mode.processes_stop.clear_shared_memory")
def test_processes_stop_all_ok(
    mock_shm,
    mock_kill_script,
    mock_get_script,
    mock_process_list,
):
    mock_process_list.side_effect = [
        ["1 a"],    # autocalib
        ["2 b"],    # epics
        ["3 c"],    # odin
    ]
    mock_get_script.return_value = ("/fake", "kill.sh")
    mock_kill_script.return_value = True
    mock_shm.return_value = True


    result = processes_stop(confirm=False)

    assert result is True

@patch("pyxspress.switch_mode.processes_stop.process_list")
@patch("pyxspress.switch_mode.processes_stop.get_stop_script")
@patch("pyxspress.switch_mode.processes_stop.kill_script")
@patch("pyxspress.switch_mode.processes_stop.clear_shared_memory")
def test_processes_stop_partial_failure(
    mock_shm,
    mock_kill_script,
    mock_get_script,
    mock_process_list,
):
    mock_process_list.side_effect = [
        ["1 a"],
        ["2 b"],
        ["3 c"],
    ]
    mock_get_script.return_value = ("/fake", "kill.sh")
    mock_kill_script.side_effect = [True, False, True]
    mock_shm.return_value = True


    result = processes_stop(confirm=False)

    assert result is False
