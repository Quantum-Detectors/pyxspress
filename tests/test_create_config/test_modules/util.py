"""
General test utility functions

"""

import os
from pathlib import Path


def get_test_file_directory() -> Path:
    dirname = os.path.dirname(__file__)
    test_file_dir = os.path.normpath(os.path.join(dirname, "../../../test_files"))
    return Path(test_file_dir)


def get_8ch_Mk2_test_file_directory() -> Path:
    return get_test_file_directory() / "config_8Ch_Mk2"


def get_8ch_Mk2_file_string(file_name: str) -> str:
    """Get the contents of a file from the example 8 channel system files

    Args:
        file_name (str): Name of file

    Returns:
        str: Contents of example file
    """
    with open(get_8ch_Mk2_test_file_directory() / file_name) as test_file:
        contents = test_file.read()

    return contents

def get_8ch_Mk1_test_file_directory() -> Path:
    return get_test_file_directory() / "config_8Ch_Mk1"


def get_8ch_Mk1_file_string(file_name: str) -> str:
    """Get the contents of a file from the example 8 channel system files

    Args:
        file_name (str): Name of file

    Returns:
        str: Contents of example file
    """
    with open(get_8ch_Mk1_test_file_directory() / file_name) as test_file:
        contents = test_file.read()

    return contents
