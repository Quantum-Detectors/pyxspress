import shutil
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from pyxspress.util.util import get_module_logger

logger = get_module_logger(sub_module="substitutions")


def _odin_data_template(num_cards: int):
    od_temp_string = ""
    for i in range(num_cards):
        od_temp_string += (
            f'    {{ "XSPRESS", ":OD{i + 1}:", "ODN.OD", "1", "{i}", "{num_cards}" }}\n'
        )

    return od_temp_string.strip("\n")


def _xspress_channel_template(num_chans: int):
    xspress_chan_temp_string = ""
    for i in range(num_chans):
        xspress_chan_temp_string += (
            '    { "XSPRESS", ":CAM:", "ODN.CAM", "'
            f'{i}", "{i + 1}", "{num_chans}", "1" }}\n'
        )
    return xspress_chan_temp_string.strip("\n")


def _xspress_fem_template(num_cards: int):
    xspress_fem_string = ""
    for i in range(num_cards):
        xspress_fem_string += (
            f'    {{ "XSPRESS", ":CAM:", "ODN.CAM", "{i}", "{num_cards}", "1" }}\n'
        )
    return xspress_fem_string.strip("\n")


def _odin_procserv_template(num_cards: int):
    odin_procserv_string = '    { "ODN", "OdinServer", "XSP-ODN-01" }\n'
    odin_procserv_string += '    { "ODN", "MetaWriter", "XSP-ODN-02" }\n'
    odin_procserv_string += '    { "ODN", "ControlServer", "XSP-ODN-03" }\n'
    odin_procserv_string += '    { "ODN", "LiveViewMerge", "XSP-ODN-04" }\n'

    for i in range(num_cards):
        odin_procserv_string += (
            f'    {{ "ODN", "FrameReceiver{i + 1}", '
            f'"XSP-ODN-{((i + 1) * 2) + 3:02d}" }}\n'
        )
        odin_procserv_string += (
            f'    {{ "ODN", "FrameProcessor{i + 1}", '
            f'"XSP-ODN-{((i + 1) * 2) + 4:02d}" }}\n'
        )
    odin_procserv_string += '    { "ODN", "XSPRESS", "XSPRESS" }\n'
    return odin_procserv_string.strip("\n")


def generate_ioc_db_substitutions(
    num_cards: int,
    num_chans: int,
    template_dir: Path,
    adodin_db_dir: Path,
    epics_config_dir: Path,
    test: bool,
):
    """ADOdin Xspress IOC template file

    Args:
        num_cards (int): Number of cards
        num_chans (int): Number of channels
        template_dir (Path): Template directory
        adodin_db_dir (Path): Where to write generated substitutions file
        test (bool): True if in test mode (Does not deploy to ADOdin directory)
    """
    odin_data_string = _odin_data_template(num_cards)
    xspress_channel_string = _xspress_channel_template(num_chans)
    xspress_fem_string = _xspress_fem_template(num_cards)
    odin_procserv_string = _odin_procserv_template(num_cards)

    # Replace with Jinja?
    with open(
        template_dir / "xspress_expanded.substitutions.template"
    ) as xspress_expanded_temp:
        xspress_expanded_string = xspress_expanded_temp.read()
        xspress_expanded_string = xspress_expanded_string.replace(
            "{chans}", str(num_chans)
        )
        xspress_expanded_string = xspress_expanded_string.replace(
            "{cards}", str(num_cards)
        )
        xspress_expanded_string = xspress_expanded_string.replace(
            "{odin_data_template}", odin_data_string
        )
        xspress_expanded_string = xspress_expanded_string.replace(
            "{xspress_channel_template}", xspress_channel_string
        )
        xspress_expanded_string = xspress_expanded_string.replace(
            "{xspress_fem_template}", xspress_fem_string
        )
        xspress_expanded_string = xspress_expanded_string.replace(
            "{odin_procserv_template}", odin_procserv_string
        )

    # We write the file to the `/odin/epics/config` directory so it can be
    # re-deployed on the target server if ADOdin is rebuilt from source
    # without having to re-create the file again
    file_path = Path(epics_config_dir / "xspress_expanded.substitutions")
    logger.info(f"Writing substitutions file {file_path}")
    with open(file_path, "w") as xspress_expanded_file:
        xspress_expanded_file.write(xspress_expanded_string)

    if not test:
        # If the ADOdin directory already exists then we can also deploy the
        # IOC template file directory and rebuild ADOdin
        if adodin_db_dir.exists() and adodin_db_dir.is_dir():
            shutil.copy(file_path, adodin_db_dir)


def generate_ioc_boot_script(
    template_dir: Path, adodin_ioc_boot_dir: Path, num_processors: int
):
    """Generate the ADOdin IOC boot script

    This needs to be configured based on the number of Odin processors
    that are running.

    Args:
        template_dir (Path): Source template directory
        adodin_ioc_boot_dir (Path): ADOdin source IOC boot directory for Xspress
        num_processors (int): Number of Odin data processors
    """
    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template("adodin_ioc.boot.template")

    ioc_boot = template.render(num_processors=num_processors)

    boot_file_path = adodin_ioc_boot_dir / "stxspress.boot"
    logger.info(f"Writing ADOdin IOC boot file: {boot_file_path}")
    with open(boot_file_path, "w") as ioc_boot_file:
        # Add trailing newline as otherwise it gets skipped by IOC shell
        ioc_boot_file.write(ioc_boot + "\n")


def rebuild_adodin(adodin_path: Path) -> None:
    """Rebuild ADOdin module

    This needs to be done to copy the generate substitutions template
    and IOC boot script to the build directories of ADOdin for ADOdin
    IOC to use.

    Args:
        adodin_path (Path): ADODin support module path
    """
    try:
        subprocess.run(["make"], cwd=adodin_path, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Make command failed with error: {e}")
