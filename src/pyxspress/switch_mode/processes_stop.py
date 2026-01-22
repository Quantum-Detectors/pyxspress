import glob
import json
import logging
import subprocess
from importlib.resources import files
from typing import cast

logger = logging.getLogger(__name__)

ODIN_PROCESSES: list[str] = [
    "frameProcessor",
    "frameReceiver",
    "xspress_control",
    "xspress_meta_writer",
    "xspress_live_merge",
    "xspressControl",
    "stFrameProcessor*",
    "stFrameReceiver*",
    "stLiveViewMerge.sh",
    "stOdinServer.sh",
    "stMetaWriter.sh",
    "TcpRelay",
    "stTcpRelay.sh",
]

def process_list(proc_names: list[str]) -> list[str]:
    processes = []
    for proc_name in proc_names:
        result = subprocess.run(
            ["pgrep", "-fa", proc_name], capture_output=True, text=True
        )
        process_list = result.stdout.split("\n")[:-1]
        for process in process_list:
            logger.debug(f"Processes {process} added to list from regex {proc_name}")
            processes.append(process)
    return processes


def check_process_running(pid: str) -> bool:
    result = subprocess.run(["ps", "-p", pid], capture_output=True, text=True)
    if pid in result.stdout:
        logger.info(f"process {pid} running")
        return True
    else:
        logger.info(f"Process {pid} stopped")
        return False


def kill_process(pid: str) -> bool:
    """
    Attempt to stop a process.

    Returns:
        True  -> process is stopped
        False -> process is still running
    """
    logger.info(f"Stopping process {pid}")

    running = check_process_running(pid)
    if not running:
        logger.info(f"Process {pid} already stopped")
        return True
    else:
        kill_soft = subprocess.run(["kill", pid], capture_output=True, text=True)
        if kill_soft.returncode != 0:
            raise Exception(f"Process kill {pid} failed")

        if not check_process_running(pid):
            return True

        logger.info("Soft kill didn't work sending SIGKILL")
        force = subprocess.run(["kill", "-9", pid], capture_output=True, text=True)
        if force.returncode != 0:
            raise Exception(f"Process kill {pid} failed")
    return not check_process_running(pid)


def stop_all(procs: list[str], confirm: bool=True) -> bool:
    """
    Attempt to stop all processes.
    Confirm with user for each process if requested.

    Returns:
        True  -> all processes stopped
        False -> some processes still running
    """
    for proc in procs:
        proc_id = proc.split()[0]
        if confirm:
            while True:
                stop_proc = input(f"Process {proc} running, stop it? (y/n)").lower()
                if stop_proc == "y":
                    if not kill_process(proc_id):
                        logger.warning(
                            f"Killing process failed, please stop {proc_id} manually"
                        )
                    break
                elif stop_proc == "n":
                    logger.info(f"Not killing {proc_id}")
                    break
                else:
                    logger.warning("Invalid input, expected y or n")
        # Killing process
        else:
            if not kill_process(proc_id):
                logger.warning(
                    f"Killing process failed, please stop {proc_id} manually"
                )
                return False
    # return false if any of the processes are still running
    for proc in procs:
        proc_id = proc.split()[0]
        if check_process_running(proc_id):
            logger.warning(f"Process {proc} still running")
            return False
    return True


def kill_script(
        mode: str,
        script_dir: str | None,
        script: str,
        confirm: bool = True
        ) -> bool:
    while confirm:
        stopping_msg = f"Stopping {mode} with script {script_dir}/{script}"
        stop_procs = input(f"{stopping_msg} confirm (y/n)").lower()
        if stop_procs == 'n':
            logger.info("Not running script based on user request")
            return False
        elif stop_procs == 'y':
            logger.info("Running kill script")
            break
        else:
            logger.warning("Invalid input")

    process = subprocess.Popen(
        ["bash", script],
        cwd=script_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if process.stdout is not None:
        logger.debug(f"{mode} kill output:")
        for line in process.stdout:
            logger.debug(line)

    returncode = process.wait()
    return True if returncode == 0 else False


def clear_shared_memory() -> bool:
    xsp3_files = glob.glob("/dev/shm/xsp*")
    odin_files = glob.glob("/dev/shm/odin*")

    if xsp3_files:
        xsp3 = subprocess.run(["rm", "-f", *xsp3_files])
        no_xsp3 = xsp3.returncode
    else:
        no_xsp3 = 0
        logger.info("No matching files found")

    if odin_files:
        odin = subprocess.run(["rm", "-f", *odin_files])
        no_odin = odin.returncode
    else:
        no_odin = 0
        logger.info("No matching files found")

    if no_xsp3 == 0 and no_odin == 0:
        return True
    else:
        return False


def get_stop_script(mode: str) -> tuple[str | None, str | None]:
    config_path = files("pyxspress.switch_mode.data").joinpath("config.json")

    with open(str(config_path)) as f_json:
        scripts = json.load(f_json)
    logger.debug(f"Full config file: {scripts}")

    try:
        script_dir = scripts["stop_scripts"][mode]["directory"]
        script = scripts["stop_scripts"][mode]["command"]
    except KeyError:
        logger.warning(f"No {mode} stop script provided, stopping processes one by one")
        return None, None
    return script_dir, script


def processes_stop(confirm: bool =True) -> bool:
    # Provide a list of all names of processes you want to grep for
    # Autocalib and epics only need basic search, ODIN is more rigerous
    modes = {
        "autocalib": {
            "proc_string": ["autocalib"],
            "stopped": False,
        },
        "epics": {
            "proc_string": ["st.cmd"],
            "stopped": False,
        },
        "odin": {
            "proc_string": ODIN_PROCESSES,
            "stopped": False,
        },
    }

    # Stop all processes with scripts or with PIDs
    for mode in modes:
        proc_expression = cast(list[str], modes[mode]["proc_string"])
        # Get process list based on 'running'
        procs_running = process_list(proc_expression)

        logger.debug(
            f"{mode} has {len(procs_running)} process(es) running"
            f" these are {procs_running}"
        )
        if len(procs_running) > 0:
            script_dir, script = get_stop_script(mode)
            if script is not None:
                logger.info(f"{mode}: Stopping with script")
                stopped = kill_script(mode, script_dir, script, confirm)
            else:
                logger.info(f"{mode}: Stopping each process ")
                # Kill process with confirm
                stopped = stop_all(procs_running, confirm)
        else:
            logger.info(f"No {mode} processes running")
            stopped = True
        logger.debug(f"{mode} exited with {stopped}")
        modes[mode]["stopped"] = stopped

    odin_stopped = modes["odin"]["stopped"]
    epics_stopped = modes["epics"]["stopped"]
    calib_stopped = modes["autocalib"]["stopped"]

    logger.info(
        f"Odin stopped: {odin_stopped}, "
        f"Epics stopped: {epics_stopped}, "
        f"Autocalib stopped: {calib_stopped}"
    )

    if odin_stopped and calib_stopped and epics_stopped:
        logger.info("All processes stopped")
        all_stopped = True
    else:
        logger.warning("Some processes failed to stop")
        all_stopped = False
        # Not clearing the shared memory as processes still running
        return all_stopped

    shm_msg = (
        "Shared memory cleared"
        if clear_shared_memory()
        else "Shared memory failed to clear"
    )
    logger.info(shm_msg)
    return all_stopped

