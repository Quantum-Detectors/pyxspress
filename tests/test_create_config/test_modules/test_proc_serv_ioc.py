from unittest.mock import patch

from pyxspress.create_config.modules.proc_serv_ioc import (
    _db_load_records,
    _odin_ports,
    _post_IOC,
    _proc_serv_control,
    proc_serv_ioc,
    proc_serv_ioc_yaml,
)


def test_odin_ports() -> None:
    num_cards = 2
    result = _odin_ports(num_cards)
    chan_base = 4010
    for i in range(num_cards):
        odin_ports_string = (
            f'drvAsynIPPortConfigure("OdinFR{i + 1}Port", '
            f'"localhost:{chan_base + (i * 2)}", 100, 0, 0)\n'
        )
        odin_ports_string += (
            f'drvAsynIPPortConfigure("OdinFP{i + 1}Port", '
            f'"localhost:{chan_base + (i * 2) + 1}", 100, 0, 0)\n'
        )
        assert odin_ports_string in result
        assert (
            'drvAsynIPPortConfigure("OdinServerPort", "localhost:4001", 100, 0, 0)\n'
            in result
        )


def test_db_load_records() -> None:
    num_cards = 2
    proc_temp = 'dbLoadRecords "${PROCSERVCONTROL}/db/procServControl.template",'
    result = _db_load_records(num_cards)
    for i in range(num_cards):
        load_records_str = (
            proc_temp + f'"P=XSP-ODN-{(i * 2) + 5:02d}, PORT=OdinFR{i + 1}Port"\n'
        )
        load_records_str += (
            proc_temp + f'"P=XSP-ODN-{(i * 2) + 6:02d}, PORT=OdinFP{i + 1}Port"\n'
        )
        assert load_records_str in result
        assert '"P=XSPRESS, PORT=ADOdinPort"' in result


def test_proc_serv_control() -> None:
    num_cards = 2
    total_records = 4 + (2 * num_cards)
    result = _proc_serv_control(num_cards)
    for i in range(total_records):
        # text without newline
        proc_serv_string = f'seq(procServControl, "P=XSP-ODN-{i + 1:02d}")'
        assert proc_serv_string in result


def test_post_IOC() -> None:
    num_cards = 2
    result = _post_IOC(num_cards)
    for i in range(num_cards):
        post_IOC_string = (
            f'dbpf "XSP-ODN-{(i * 2) + 5:02d}:IOCNAME" "Odin frame receiver {i + 1}"\n'
        )
        post_IOC_string += (
            f'dbpf "XSP-ODN-{(i * 2) + 6:02d}:IOCNAME" "Odin frame processor {i + 1}"\n'
        )
        assert post_IOC_string in result


@patch("pyxspress.create_config.modules.proc_serv_ioc._odin_ports")
@patch("pyxspress.create_config.modules.proc_serv_ioc._db_load_records")
@patch("pyxspress.create_config.modules.proc_serv_ioc._proc_serv_control")
@patch("pyxspress.create_config.modules.proc_serv_ioc._post_IOC")
def test_proc_serv_ioc(
    mock_post_ioc,
    mock_proc_serv_control,
    mock_db_load_records,
    mock_odin_ports,
    template_dir,
    tmp_path,
) -> None:
    num_cards = 2
    mock_post_ioc.return_value = "<mock_post_IOC>"
    mock_proc_serv_control.return_value = "<mock_proc_serv_control>"
    mock_db_load_records.return_value = "<mock_db_load_records>"
    mock_odin_ports.return_value = "<mock_odin_ports>"

    proc_serv_ioc(num_cards, template_dir, tmp_path)

    assert mock_post_ioc.called
    assert mock_proc_serv_control.called
    assert mock_db_load_records.called
    assert mock_odin_ports.called

    assert (tmp_path / "proc_serv_ioc.boot").exists()
    text = (tmp_path / "proc_serv_ioc.boot").read_text()
    assert "{}" not in text
    assert "<mock_post_IOC>" in text
    assert "<mock_proc_serv_control>" in text
    assert "<mock_db_load_records>" in text
    assert "<mock_odin_ports>" in text


def test_proc_serv_ioc_yaml(template_dir, tmp_path) -> None:
    num_cards = 2
    proc_serv_ioc_yaml(num_cards, template_dir, tmp_path)

    assert (tmp_path / "odin_proc_serv_ioc.yaml").exists()
    text = (tmp_path / "odin_proc_serv_ioc.yaml").read_text()
    assert "{}" not in text
    assert f"{(num_cards * 2) + 4}" in text
