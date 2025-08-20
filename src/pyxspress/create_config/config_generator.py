import os
import shutil
from collections.abc import Callable
from glob import glob
from pathlib import Path
from typing import Any

from pyxspress.create_config.modules.create_expanded_substitutions import (
    xspress_expanded_substitutions,
)
from pyxspress.create_config.modules.create_frame_processors import (
    frame_processor,
    frame_processor_json,
)
from pyxspress.create_config.modules.create_frame_receivers import (
    frame_reciever,
    frame_reciever_json,
)
from pyxspress.create_config.modules.create_gui import create_gui
from pyxspress.create_config.modules.create_meta_liveView import (
    live_view_file,
    meta_writer_file,
)
from pyxspress.create_config.modules.create_odin_launch_script import launch_n_chan
from pyxspress.create_config.modules.create_proc_serv_ioc import (
    proc_serv_ioc,
    proc_serv_ioc_yaml,
)
from pyxspress.create_config.modules.create_server_config import odin_server_config
from pyxspress.util import Loggable


class ConfigGenerator(Loggable):
    config_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    common_dir = config_dir / "common"
    module_dir = config_dir / "modules"
    template_dir = config_dir / "templates"

    # ADOdin paths
    adodin_dir = Path("/odin/epics/support/ADOdin")
    adodin_ioc_db_dir = adodin_dir / "iocs/xspress/xspressApp/Db"
    adodin_edl_dir = adodin_dir / "iocs/xspress/xspressApp/opi/edl"

    def __init__(
        self,
        num_cards: int,
        num_chans: int,
        mark: int,
        odin_path: Path,
        epics_path: Path,
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
            test (bool): Testing flag to build config in place.
        """
        super().__init__()

        # TODO: validate arguments
        self.num_cards = num_cards
        self.num_chans = num_chans
        self.mark = mark
        self.odin_path = odin_path
        self.epics_path = epics_path
        self.test = test

        if self.test:
            # If testing then update the EDL directory to just use the EPICS dir
            self.adodin_edl_dir = self.epics_path

    def clean(self) -> None:
        """Clean the target configuration directory"""
        if self.odin_path.exists() and self.odin_path.is_dir():
            self.logger.info(f"Cleaning directory: {self.odin_path}")
            shutil.rmtree(self.odin_path)

    def generate(self) -> None:
        """Generate the configuration for Odin and related software"""
        self.logger.info(
            "Generating configuration files.\n\n"
            f"Configuration:\n"
            f"  - Cards: {self.num_cards}\n"
            f"  - Channels: {self.num_chans}\n"
            f"  - Generation: {self.mark}\n"
            f"  - Odin config path: {self.odin_path}\n"
            f"  - EPICS config path: {self.epics_path}\n"
        )

        # Create the Odin configuration directory if it doesn't exist
        if not self.odin_path.exists():
            self.logger.info(f"Creating config directory: {self.odin_path}")
            os.mkdir(self.odin_path)

        # Standard config files
        self.__copy_common_files()

        # Generated configuration
        funcs_with_cards_and_channels: list[Callable[[int, int, Path, Path], Any]] = [
            odin_server_config,
            meta_writer_file,
            launch_n_chan,
        ]
        funcs_with_cards_only: list[Callable[[int, Path, Path], Any]] = [
            live_view_file,
            proc_serv_ioc,
            proc_serv_ioc_yaml,
            frame_processor,
            frame_processor_json,
            frame_reciever,
            frame_reciever_json,
        ]

        for func_cards_and_channels in funcs_with_cards_and_channels:
            func_cards_and_channels(
                self.num_cards, self.num_chans, self.template_dir, self.odin_path
            )

        for func_with_cards_only in funcs_with_cards_only:
            func_with_cards_only(self.num_cards, self.template_dir, self.odin_path)

        # IOC template
        xspress_expanded_substitutions(
            self.num_cards,
            self.num_chans,
            self.template_dir,
            self.adodin_dir,
            self.adodin_ioc_db_dir,
            self.epics_path,
            self.test,
        )

        # GUI
        create_gui(self.num_cards, self.template_dir, self.adodin_edl_dir)

        self.logger.info("Config generation complete!")

    def __copy_common_files(self) -> None:
        self.logger.info("Copying common shell scripts")
        for file in glob(f"{self.common_dir}/*.sh"):
            self.logger.debug(f"Copying {file} to {self.odin_path}")
            shutil.copy2(file, self.odin_path)

        self.logger.info("Copying common Odin configuration files")
        for file in glob(f"{self.common_dir}/*.json"):
            self.logger.debug(f"Copying {file} to {self.odin_path}")
            shutil.copy2(file, self.odin_path)
