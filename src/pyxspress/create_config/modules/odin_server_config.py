from pathlib import Path


def _daq_endpoints(num_cards):
    daq_ep_str = ""
    for card in range(num_cards):
        daq_ep_str += f"tcp://127.0.0.1:151{50 + card},"
    return daq_ep_str.strip(",")


def _processor_endpoints(num_cards):
    fp_ep_str = ""
    for card in range(num_cards):
        fp_ep_str += f"127.0.0.1:10{4 + (10 * card):03d},"
    return fp_ep_str.strip(",")


def _receiver_endpoints(num_cards):
    fr_ep_str = ""
    for card in range(num_cards):
        fr_ep_str += f"127.0.0.1:10{(10 * card):03d},"
    return fr_ep_str.strip(",")


def odin_server_config(
    num_cards: int,
    num_chans: int,
    tcp_relay_server: bool,
    template_dir: Path,
    target_dir: Path,
) -> None:
    """Generate the Odin Python server configuration file

    Args:
        num_cards (int): Number of cards in Xspress system
        num_chans (int): Number of channels in Xspress system
        tcp_relay_server (bool): Whether to use TCP relay server
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """
    fp_endpoints = _processor_endpoints(num_cards)
    fr_endpoints = _receiver_endpoints(num_cards)
    adapter_endpoints = _daq_endpoints(num_cards)
    processes = str(num_cards)

    with open(template_dir / "odin_server.cfg.template") as server_config:
        server_string = server_config.read()

    # TODO: use jinja?
    server_string = server_string.replace("{cards}", str(num_cards))
    server_string = server_string.replace("{chans}", str(num_chans))
    server_string = server_string.replace("{fp_endpoints}", fp_endpoints)
    server_string = server_string.replace("{fr_endpoints}", fr_endpoints)
    server_string = server_string.replace("{adapter_endpoints}", adapter_endpoints)
    server_string = server_string.replace("{processes}", processes)
    server_string = server_string.replace("{use_tcp_relay}", str(int(tcp_relay_server)))

    with open(target_dir / "odin_server.cfg", "w") as server_config_file:
        server_config_file.write(server_string)
