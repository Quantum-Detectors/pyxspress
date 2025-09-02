from pathlib import Path


def _odin_ports(num_cards):
    odin_ports_string = (
        'drvAsynIPPortConfigure("OdinServerPort", "localhost:4001", 100, 0, 0)\n'
    )
    odin_ports_string += (
        'drvAsynIPPortConfigure("OdinMetaPort", "localhost:4002", 100, 0, 0)\n'
    )
    odin_ports_string += (
        'drvAsynIPPortConfigure("ControlServerPort", "localhost:4003", 100, 0, 0)\n'
    )
    odin_ports_string += (
        'drvAsynIPPortConfigure("OdinLVPort", "localhost:4004", 100, 0, 0)\n'
    )
    odin_ports_string += (
        'drvAsynIPPortConfigure("ADOdinPort", "localhost:4005", 100, 0, 0)\n'
    )
    chan_base = 4010
    for i in range(num_cards):
        odin_ports_string += (
            f'drvAsynIPPortConfigure("OdinFR{i + 1}Port", '
            f'"localhost:{chan_base + (i * 2)}", 100, 0, 0)\n'
        )
        odin_ports_string += (
            f'drvAsynIPPortConfigure("OdinFP{i + 1}Port", '
            f'"localhost:{chan_base + (i * 2) + 1}", 100, 0, 0)\n'
        )
    return odin_ports_string


def _db_load_records(num_cards):
    proc_temp = 'dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template",'
    load_records_str = proc_temp + '"P=XSP-ODN-01, PORT=OdinServerPort"\n'
    load_records_str += proc_temp + '"P=XSP-ODN-02, PORT=OdinMetaPort"\n'
    load_records_str += proc_temp + '"P=XSP-ODN-03, PORT=ControlServerPort"\n'
    load_records_str += proc_temp + '"P=XSP-ODN-04, PORT=OdinLVPort"\n'
    for i in range(num_cards):
        load_records_str += (
            proc_temp + f'"P=XSP-ODN-{(i * 2) + 5:02d}, PORT=OdinFR{i + 1}Port"\n'
        )
        load_records_str += (
            proc_temp + f'"P=XSP-ODN-{(i * 2) + 6:02d}, PORT=OdinFP{i + 1}Port"\n'
        )
    load_records_str += proc_temp + '"P=XSPRESS, PORT=ADOdinPort"'

    return load_records_str


def _proc_serv_control(num_cards):
    total_records = 4 + (2 * num_cards)
    proc_serv_string = ""
    for i in range(total_records):
        proc_serv_string += f'seq(procServControl, "P=XSP-ODN-{i + 1:02d}")\n'

    return proc_serv_string.strip("\n")


def _post_IOC(num_cards):
    post_IOC_string = 'dbpf "XSP-ODN-01:IOCNAME" "Odin server"\n'
    post_IOC_string += 'dbpf "XSP-ODN-02:IOCNAME" "Odin meta writer"\n'
    post_IOC_string += 'dbpf "XSP-ODN-03:IOCNAME" "Odin control server"\n'
    post_IOC_string += 'dbpf "XSP-ODN-04:IOCNAME" "Odin live view"\n'
    for i in range(num_cards):
        post_IOC_string += (
            f'dbpf "XSP-ODN-{(i * 2) + 5:02d}:IOCNAME" "Odin frame receiver {i + 1}"\n'
        )
        post_IOC_string += (
            f'dbpf "XSP-ODN-{(i * 2) + 6:02d}:IOCNAME" "Odin frame processor {i + 1}"\n'
        )
    post_IOC_string += 'dbpf "XSPRESS:IOCNAME" "Xspress ADOdin"'

    return post_IOC_string


def proc_serv_ioc(num_cards: int, template_dir: Path, target_dir: Path):
    """Create the procServIoc config file

    Args:
        num_cards (int): Number of cards
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """
    odin_ports_str = _odin_ports(num_cards)
    db_load_str = _db_load_records(num_cards)
    proc_serv_str = _proc_serv_control(num_cards)
    post_ioc_str = _post_IOC(num_cards)

    with open(template_dir / "proc_serv_ioc.boot.template") as proc_serv_temp:
        proc_serv_file_string = proc_serv_temp.read()
        proc_serv_file_string = proc_serv_file_string.replace(
            "{odin_ports}", odin_ports_str
        )
        proc_serv_file_string = proc_serv_file_string.replace(
            "{db_load_records}", db_load_str
        )
        proc_serv_file_string = proc_serv_file_string.replace(
            "{proc_serv_control}", proc_serv_str
        )
        proc_serv_file_string = proc_serv_file_string.replace(
            "{post_IOC}", post_ioc_str
        )

    with open(target_dir / "proc_serv_ioc.boot", "w") as proc_serv_file:
        proc_serv_file.write(proc_serv_file_string)


def proc_serv_ioc_yaml(num_cards: int, template_dir: Path, target_dir: Path):
    """Create the procServIOC YAML configuration

    Args:
        num_cards (int): Number of cards
        template_dir (Path): Template directory
        target_dir (Path): Output directory
    """
    processes = (num_cards * 2) + 4
    with open(template_dir / "odin_proc_serv_ioc.yaml.template") as yaml_temp:
        yaml_string = yaml_temp.read()

    yaml_string = yaml_string.replace("{processes}", str(processes))

    with open(target_dir / "odin_proc_serv_ioc.yaml", "w") as yaml_file:
        yaml_file.write(yaml_string)
