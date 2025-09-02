from unittest.mock import patch

from pyxspress.create_config.modules.proc_serv_gui import (
    create_gui,
    generate_button,
    generate_buttons,
    logger,
    main_gui,
    make_process_dicts,
)


def test_make_process_dicts() -> None:
    num_cards = 3
    process_names = [
        "OdinServer",
        "MetaWriter",
        "ControlServer",
        "LiveViewMerge",
        "FrameReceiver1",
        "FrameProcessor1",
        "FrameReceiver2",
        "FrameProcessor2",
        "FrameReceiver3",
        "FrameProcessor3",
        "XSPRESS",
    ]

    process_dict = make_process_dicts(num_cards)
    # 4 fixed, 1 xspress, FP&FR per card
    assert len(process_dict) == num_cards * 2 + 5
    for process in process_dict:
        assert process["Name"] in process_names


def test_generate_button(template_dir) -> None:
    # Test implementation for generate_button
    with open(template_dir / "gui_button.template") as button_file_temp:
        button_template_str = button_file_temp.read()

    process = {"Name": "test", "Process": "XSP-ODN-1"}

    xpos = 10
    ypos = 20
    return_string = generate_button(button_template_str, process, xpos, ypos)
    assert f"x {xpos}\ny {ypos}" in return_string
    assert "{}" not in return_string


@patch("pyxspress.create_config.modules.proc_serv_gui.generate_button")
def test_generate_buttons_calls_generate_button(
    mock_generate_button, template_dir
) -> None:
    procs = [
        {"Name": "OdinServer", "Process": "XSP-ODN-1"},
        {"Name": "MetaWriter", "Process": "XSP-ODN-2"},
        {"Name": "XSPRESS", "Process": "XSPRESS"},
    ]

    generate_buttons(procs, template_dir)

    # Assert generate_button was called the right number of times
    assert mock_generate_button.call_count == len(procs)


def test_generate_buttons_integration(template_dir) -> None:
    prefix = "XSP-ODN-"
    standard_procs = [
        {"Name": "OdinServer", "Process": f"{prefix}1"},
        {"Name": "MetaWriter", "Process": f"{prefix}2"},
        {"Name": "ControlServer", "Process": f"{prefix}3"},
        {"Name": "LiveViewMerge", "Process": f"{prefix}4"},
        {"Name": "FrameReceiver1", "Process": f"{prefix}5"},
        {"Name": "FrameProcessor1", "Process": f"{prefix}6"},
        {"Name": "FrameReceiver2", "Process": f"{prefix}7"},
        {"Name": "FrameProcessor2", "Process": f"{prefix}8"},
        {"Name": "FrameReceiver3", "Process": f"{prefix}9"},
        {"Name": "FrameProcessor3", "Process": f"{prefix}10"},
        {"Name": "XSPRESS", "Process": "XSPRESS"},
    ]
    full_process_string = generate_buttons(standard_procs, template_dir)
    assert "OdinServer" in full_process_string
    assert "FrameProcessor3" in full_process_string


def test_main_gui(template_dir, tmp_path) -> None:
    num_cards = 2
    full_process_string = "Test Processes substitution"
    main_gui(full_process_string, num_cards, template_dir, tmp_path)

    # Add assertions to verify the behavior of main_gui
    assert (tmp_path / "ODNProcServ.edl").exists()
    text = (tmp_path / "ODNProcServ.edl").read_text()
    assert full_process_string in text
    assert "{}" not in text
    assert f"{210 + ((num_cards - 1) * 35)}" in text


def test_main_gui_returns_if_output_dir_does_not_exists(template_dir, tmp_path) -> None:
    # Mock the module logger so we can confirm that the EDL GUI generation
    # was skipped (as a warning message is printed before the function returns)
    with patch.object(logger, "warning") as mock_warning:
        main_gui("Test string", 2, template_dir, tmp_path / "does_not_exist")

    # Check the mock logger was called with the expected warning message
    mock_warning.assert_called_once_with(
        "Skipping EDL GUI generation as EDL directory does not exist"
    )


@patch("pyxspress.create_config.modules.proc_serv_gui.make_process_dicts")
@patch("pyxspress.create_config.modules.proc_serv_gui.generate_buttons")
@patch("pyxspress.create_config.modules.proc_serv_gui.main_gui")
def test_create_gui(
    mock_main_gui,
    mock_generate_buttons,
    mock_make_process_dicts,
    template_dir,
    tmp_path,
) -> None:
    num_cards = 2
    process_dict = {"Name": "test", "Process": "XSP-ODN-1"}
    full_process_string = "Full process string"

    create_gui(num_cards, template_dir, tmp_path)

    # Add assertions to verify the behavior of create_gui
    assert mock_make_process_dicts.called_with(num_cards)
    assert mock_generate_buttons.called_with(process_dict, template_dir)
    assert mock_main_gui.called_with(
        full_process_string, num_cards, template_dir, tmp_path
    )
