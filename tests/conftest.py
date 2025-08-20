"""
Conftest module

Used by pytest for global fixtures.

"""

from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

import pytest


@pytest.fixture()
def temporary_dir():
    """Create a temporary directory and return the path"""
    temp_dir = mkdtemp()
    yield Path(temp_dir)
    # Delete the tree after
    rmtree(temp_dir)
