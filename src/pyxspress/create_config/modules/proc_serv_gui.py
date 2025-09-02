from pathlib import Path

from pyxspress.util.util import get_module_logger

process_names = [
    "OdinServer",
    "MetaWriter",
    "ControlServer",
    "LiveViewMerge",
    "FrameReceiver",
    "FrameProcessor",
]
prefix = "XSP-ODN-"

logger = get_module_logger(sub_module="create_gui")


def make_process_dicts(num_cards: int) -> list[dict[str, str]]:
    """Generate process dictionaries

    Args:
        num_cards (int): Number of cards

    Returns:
        list[dict[str, str]]: List of process dictionaries containing the
                              Odin name and generic process name
    """
    processes = []

    # Fixed processes
    for j in range(4):
        processes.append(
            {
                "Name": process_names[j],
                "Process": f"{prefix}{j + 1:02d}",
            }
        )

    # Dynamic processes that depend on number of cards
    for i in range(num_cards):
        processes.append(
            {
                "Name": f"{process_names[4]}{i + 1}",
                "Process": f"{prefix}{((i + 1) * 2) + 3:02d}",
            }
        )
        processes.append(
            {
                "Name": f"{process_names[5]}{i + 1}",
                "Process": f"{prefix}{((i + 1) * 2) + 4:02d}",
            }
        )
    processes.append({"Name": "XSPRESS", "Process": "XSPRESS"})
    return processes


def generate_buttons(
    process_dict_list: list[dict[str, str]], template_dir: Path
) -> str:
    """Generate the buttons for control

    Args:
        process_dict_list (dict[str, str]): List of process dictionaries
        template_dir (Path): Template directory

    Returns:
        str: String containing generated EDL buttons
    """
    full_process_string = ""

    with open(template_dir / "gui_button.template") as button_file_temp:
        button_template_str = button_file_temp.read()

    ypos = 40
    full_process_string += generate_button(
        button_template_str, process_dict_list[0], 10, ypos
    )
    for process in process_dict_list[1:-1]:
        if int(process["Process"].split("-")[2]) % 2:
            # Left align odd buttons
            xpos = 225
        else:
            # Right align even buttons
            xpos = 10
            ypos += 35

        full_process_string += generate_button(button_template_str, process, xpos, ypos)

    full_process_string += generate_button(
        button_template_str, process_dict_list[-1], 225, 40
    )

    return full_process_string


def generate_button(
    button_template_str: str, process_dict: dict[str, str], xpos: int, ypos: int
) -> str:
    """Generate a single button

    Args:
        button_template_str (str): Button template string
        process_dict (dict[str, str]): Process dictionary
        xpos (int): X position of button
        ypos (int): Y position of button

    Returns:
        str: EDL string containing button
    """
    process_string = button_template_str.replace("{proc_serv}", process_dict["Process"])
    process_string = process_string.replace("{name}", process_dict["Name"])
    process_string = process_string.replace("{xpos1}", f"{xpos}")
    process_string = process_string.replace("{xpos2}", f"{xpos + 4}")
    process_string = process_string.replace("{xpos_but}", f"{xpos + 180}")
    process_string = process_string.replace("{ypos1}", f"{ypos}")
    process_string = process_string.replace("{ypos2}", f"{ypos + 2}")
    return process_string


def main_gui(
    full_process_string: str, num_cards: int, template_dir: Path, output_dir: Path
) -> None:
    """Generate main GUI file

    Args:
        full_process_string (str): Generated process EDL string
        num_cards (int): Number of cards
        template_dir (Path): Template directory
        output_dir (Path): Output directory for generated screen file
    """
    if not output_dir.exists() or not output_dir.is_dir():
        logger.warning("Skipping EDL GUI generation as EDL directory does not exist")
        return

    height = 210 + ((num_cards - 1) * 35)
    button_pos = height - 65
    exit_button_pos = height - 30

    with open(template_dir / "gui_proc_serv.edl.template") as proc_file_temp:
        proc_file_string = proc_file_temp.read()

    proc_file_string = proc_file_string.replace("{processes}", full_process_string)
    proc_file_string = proc_file_string.replace("{screen_height}", str(height))
    proc_file_string = proc_file_string.replace("{y_pos_buttons}", str(button_pos))
    proc_file_string = proc_file_string.replace("{y_pos_exit}", str(exit_button_pos))

    edl_filepath = output_dir / "ODNProcServ.edl"
    logger.info(f"Writing EDL file to {edl_filepath}")
    with open(edl_filepath, "w") as edl_file:
        edl_file.write(proc_file_string)


def create_gui(num_cards: int, template_dir: Path, output_dir: Path):
    """Create the procServ GUI for controlling the Odin processes
    using provServ

    Args:
        num_cards (int): Number of cards (as 1 FR/FP pair per 1 card)
        template_dir (Path): Template directory
        output_dir (Path): Output directory for GUI file
    """
    process_dict = make_process_dicts(num_cards)
    full_process_string = generate_buttons(process_dict, template_dir)
    main_gui(full_process_string, num_cards, template_dir, output_dir)
