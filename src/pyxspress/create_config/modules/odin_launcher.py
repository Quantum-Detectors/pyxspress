import os
from pathlib import Path


def _odin_processes(num_cards):
    odin_process_string = "procServ -P 4001 /odin/config/stOdinServer.sh\n"
    odin_process_string += "procServ -P 4002 /odin/config/stMetaWriter.sh\n"
    odin_process_string += "procServ -P 4003 /odin/config/stControlServer.sh\n"
    odin_process_string += "procServ -P 4004 /odin/config/stLiveViewMerge.sh\n\n"
    odin_process_string += (
        "# ADOdin\nprocServ -P 4005 /odin/config/stXspressADOdin.sh\n\n"
    )
    base_port = 4010
    odin_process_string += "# Frame Reciever and Process pairs\n"
    for i in range(num_cards):
        odin_process_string += (
            f"procServ -P {base_port + (i * 2)} "
            f"/odin/config/stFrameReceiver{i + 1}.sh\n"
        )
        odin_process_string += (
            f"procServ -P {base_port + (i * 2) + 1} "
            f"/odin/config/stFrameProcessor{i + 1}.sh\n"
        )
    return odin_process_string


def launch_n_chan(
    num_cards: int, num_chans: int, template_dir: Path, target_dir: Path
) -> None:
    """Create the launch shell script file

    Args:
        num_cards (int): Number of cards in Xspress system
        num_chans (int): Number of channels in Xspress system
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """
    odin_processes_str = _odin_processes(num_cards)
    with open(template_dir / "launch_nchan_odin.sh.template") as launch_temp:
        launch_file_string = launch_temp.read()

    launch_file_string = launch_file_string.replace("{chans}", str(num_chans))
    launch_file_string = launch_file_string.replace(
        "{odin_processes}", odin_processes_str
    )

    target_filepath = target_dir / f"launch_{num_chans}chan_odin.sh"
    with open(target_filepath, "w") as launch_file:
        launch_file.write(launch_file_string)

    # Make executable
    os.chmod(target_filepath, 0o755)
