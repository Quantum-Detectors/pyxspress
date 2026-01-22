import json
import os
import subprocess
from importlib.resources import files

config_path = files("pyxspress.switch_mode.data").joinpath("config.json")


def get_script_dir(mode: str) -> tuple[str | None, str]:
    with open(str(config_path)) as f_json:
        scripts = json.load(f_json)
    script_dir = scripts["start_scripts"][mode]["directory"]
    script = scripts["start_scripts"][mode]["command"]
    return script_dir, script


def start_new_mode(mode: str) -> int:
    # Get the directory and start script from the json
    script_dir, script = get_script_dir(mode)

    # Expand ~/ and environment variables
    if script_dir:
        script_dir = os.path.expandvars(os.path.expanduser(script_dir))
        if not os.path.isdir(script_dir):
            raise FileNotFoundError(f"Directory does not exist: {script_dir}")
    else:
        script_dir = None  # autocalib don't care

    process = subprocess.Popen(
        [script],
        cwd=script_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    # Stream output live
    if process.stdout is not None:
        for line in process.stdout:
            print(line, end="")
    process.wait()
    return process.returncode
