import os
from pathlib import Path


def _odin_processes(num_cards: int) -> str:
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


def _tcp_relay_string(tcp_relay_server: bool, num_cards: int) -> str:
    if not tcp_relay_server:
        return ""

    # Initial values
    proc_serv_port_minus_one = 8000
    start_port_minus_one = 13000

    relay_string = "\n# TCP relay servers"
    for card_num in range(1, num_cards + 1):
        relay_string += (
            f"\nprocServ -P {proc_serv_port_minus_one + card_num} "
            "/odin/config/stTcpRelay.sh "
            f"192.168.0.{card_num + 1}:30125 {start_port_minus_one + card_num}"
        )
    return relay_string


def launch_n_chan(
    num_cards: int,
    num_chans: int,
    tcp_relay_server: bool,
    template_dir: Path,
    target_dir: Path,
) -> None:
    """Create the launch shell script file

    Args:
        num_cards (int): Number of cards in Xspress system
        num_chans (int): Number of channels in Xspress system
        tcp_relay_server (bool): Whether to use TCP relay server
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """
    with open(template_dir / "launch_nchan_odin.sh.template") as launch_temp:
        launch_file_string = launch_temp.read()

    # Strings to substitute
    odin_processes_str = _odin_processes(num_cards)
    tcp_relay_str = _tcp_relay_string(tcp_relay_server, num_cards)

    launch_file_string = launch_file_string.replace("{chans}", str(num_chans))
    launch_file_string = launch_file_string.replace(
        "{odin_processes}", odin_processes_str
    )
    launch_file_string = launch_file_string.replace(
        "{tcp_relay_servers}", tcp_relay_str
    )

    target_filepath = target_dir / f"launch_{num_chans}chan_odin.sh"
    with open(target_filepath, "w") as launch_file:
        launch_file.write(launch_file_string)

    # Make executable
    os.chmod(target_filepath, 0o755)
