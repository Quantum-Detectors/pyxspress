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


@pytest.fixture
def example_mca_metadata_filepath():
    dirname = os.path.dirname(__file__)
    template_dir = os.path.join(
        dirname, "../test_files/example_mca_data/test-mca-1_meta.h5"
    )
    return Path(template_dir)


@pytest.fixture
def example_mca_A_filepath():
    dirname = os.path.dirname(__file__)
    template_dir = os.path.join(
        dirname, "../test_files/example_mca_data/test-mca-1_A_000000.h5"
    )
    return Path(template_dir)
