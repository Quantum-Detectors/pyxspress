import os
import shutil
from collections.abc import Callable
from glob import glob
from pathlib import Path
from typing import Any

from pyxspress.create_config.modules.adodin_config import (
    generate_ioc_boot_script,
    generate_ioc_db_substitutions,
    rebuild_adodin,
)
from pyxspress.create_config.modules.fp_config import (
    create_fp_config_file,
    create_fp_launch_script,
)
from pyxspress.create_config.modules.fr_config import (
    create_fr_config_file,
    create_fr_launch_script,
)
from pyxspress.create_config.modules.meta_config import (
    create_live_view_launch_script,
    create_meta_writer_launch_script,
)
from pyxspress.create_config.modules.odin_launcher import launch_n_chan
from pyxspress.create_config.modules.odin_server_config import odin_server_config
from pyxspress.create_config.modules.proc_serv_gui import create_gui
from pyxspress.create_config.modules.proc_serv_ioc import (
    proc_serv_ioc,
    proc_serv_ioc_yaml,
)
from pyxspress.util import Loggable


class ConfigGenerator(Loggable):
    config_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    common_dir = config_dir / "common"
    module_dir = config_dir / "modules"
    optional_script_dir = config_dir / "optional"
    template_dir = config_dir / "templates"

    # Installed ADOdin paths
    adodin_dir = Path("/odin/epics/support/ADOdin")
    adodin_ioc_boot_dir = adodin_dir / "iocs/xspress/iocBoot/iocxspress"
    adodin_ioc_db_dir = adodin_dir / "iocs/xspress/xspressApp/Db"
    adodin_edl_dir = adodin_dir / "iocs/xspress/xspressApp/opi/edl"

    def __init__(
        self,
        num_cards: int,
        num_chans: int,
        mark: int,
        marker_channels: bool,
        odin_path: Path,
        epics_path: Path,
        tcp_relay: bool,
        test: bool,
    ) -> None:
        """Create a config generator

        This generates all of the runtime configuration files required for Odin.

        It also creates the ADOdin IOC template file based on the number of channels
        needed and procServControl screens.

        Args:
            num_cards (int): Number of cards in Xspress system
            num_chans (int): Number of channels in Xspress system
            mark (int): X3X generation (Mk1 or 2)
            odin_path (Path): Odin config output directory
            epics_path (Path): EPICS config output directory
            tcp_relay (bool): Add TCP relay server if true
            test (bool): Testing flag to build config in place.
        """
        super().__init__()

        # TODO: validate arguments
        self.num_cards = num_cards
        self.num_chans = num_chans
        self.mark = mark
        self.marker_channels = marker_channels
        self.odin_path = odin_path
        self.epics_path = epics_path
        self.tcp_relay = tcp_relay
        self.test = test

        # TODO change this based on generation of system
        # Assuming Mk2 requires additional processor for optimisation
        if mark == 2:
            self.num_processors = num_cards
        else:
            self.num_processors = num_cards

        # Generated configuration functions with common arguments
        self.funcs_with_cards_and_channels: list[
            Callable[[int, int, Path, Path], Any]
        ] = [
            create_meta_writer_launch_script,
        ]
        self.funcs_with_cards_only: list[Callable[[int, Path, Path], Any]] = [
            create_live_view_launch_script,
            proc_serv_ioc,
            proc_serv_ioc_yaml,
            create_fp_launch_script,
            create_fr_launch_script,
            create_fr_config_file,
        ]

        self.funcs_with_cards_channels_and_tcp_relay_server: list[
            Callable[[int, int, bool, Path, Path], Any]
        ] = [
            launch_n_chan,
            odin_server_config,
        ]

        if self.test:
            # If testing then update the EDL directory to just use the EPICS dir
            self.adodin_edl_dir = self.epics_path
            self.adodin_ioc_boot_dir = self.epics_path

    def clean(self) -> None:
        """Clean the target configuration directory"""
        if self.odin_path.exists() and self.odin_path.is_dir():
            self.logger.info(f"Cleaning directory: {self.odin_path}")
            shutil.rmtree(self.odin_path)

    def generate(self) -> None:
        """Generate the configuration for Odin and related software"""
        if self.marker_channels:
            marker_str = "  - Using marker channels\n"
        else:
            marker_str = ""

        self.logger.info(
            "Generating configuration files.\n\n"
            f"Configuration:\n"
            f"  - Cards: {self.num_cards}\n"
            f"  - Channels: {self.num_chans}\n"
            f"{marker_str}"
            f"  - Generation: {self.mark}\n"
            f"  - TCP relay server: {self.tcp_relay}\n"
            f"  - Odin config path: {self.odin_path}\n"
            f"  - EPICS config path: {self.epics_path}\n"
        )

        # Create the Odin configuration directory if it doesn't exist
        if not self.odin_path.exists():
            self.logger.info(f"Creating config directory: {self.odin_path}")
            os.mkdir(self.odin_path)

        self.__copy_common_files()

        self.__copy_optional_files()

        for func_c_and_ch in self.funcs_with_cards_and_channels:
            func_c_and_ch(
                self.num_cards, self.num_chans, self.template_dir, self.odin_path
            )

        for func_c_only in self.funcs_with_cards_only:
            func_c_only(self.num_cards, self.template_dir, self.odin_path)

        for func_c_ch_and_tcp in self.funcs_with_cards_channels_and_tcp_relay_server:
            func_c_ch_and_tcp(
                self.num_cards,
                self.num_chans,
                self.tcp_relay,
                self.template_dir,
                self.odin_path,
            )

        create_fp_config_file(
            self.num_cards, self.template_dir, self.odin_path, self.marker_channels
        )

        self.__create_adodin_ioc_files()

        self.logger.info("Config generation complete!")

    def __create_adodin_ioc_files(self) -> None:
        generate_ioc_db_substitutions(
            self.num_cards,
            self.num_chans,
            self.template_dir,
            self.adodin_ioc_db_dir,
            self.epics_path,
            self.test,
        )

        generate_ioc_boot_script(
            self.template_dir, self.adodin_ioc_boot_dir, self.num_processors
        )

        create_gui(self.num_cards, self.template_dir, self.adodin_edl_dir)

        # Rebuild ADOdin if not testing
        if not self.test:
            rebuild_adodin(self.adodin_dir)

    def __copy_common_files(self) -> None:
        self.logger.info("Copying common shell scripts")

        for file in glob(f"{self.common_dir}/*.sh"):
            self.logger.debug(f"Copying {file} to {self.odin_path}")
            shutil.copy2(file, self.odin_path)

        self.logger.info("Copying common Odin configuration files")
        for file in glob(f"{self.common_dir}/*.json"):
            self.logger.debug(f"Copying {file} to {self.odin_path}")
            shutil.copy2(file, self.odin_path)

    def __copy_optional_files(self) -> None:
        self.logger.info("Copying optional shell scripts")

        if self.tcp_relay:
            self.logger.info("Copying TCP relay script")
            shutil.copy2(
                f"{self.optional_script_dir / 'stTcpRelay.sh'}", self.odin_path
            )
