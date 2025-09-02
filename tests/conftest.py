"""
Conftest module

Used by pytest for global fixtures.

"""

import os
from pathlib import Path

import pytest


@pytest.fixture
def template_dir():
    dirname = os.path.dirname(__file__)
    template_dir = os.path.join(dirname, "../src/pyxspress/create_config/templates")
    return Path(template_dir)
