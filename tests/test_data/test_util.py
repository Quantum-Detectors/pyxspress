from unittest.mock import MagicMock, patch

from pytest import raises

from pyxspress.data import get_file_reader, get_matching_xspress_files
from pyxspress.data.xspress_list_file_reader import XspressListFileReader
from pyxspress.data.xspress_mca_file_reader import XspressMCAFileReader


def test_get_file_reader_raises_FileNotFoundError_for_not_existing_path(
    tmp_path,
) -> None:
    with raises(FileNotFoundError):
        get_file_reader(f"{tmp_path}/no/way/this/exists.h5")


@patch("pyxspress.data.util.h5py.File")
def test_get_file_reader_returns_mca_file_reader_if_mca_keys_present(
    mock_h5py_file,
) -> None:
    mock_file_instance = MagicMock()
    mock_file_instance.keys.return_value = ["mca_0", "mca_1"]
    mock_h5py_file.return_value = mock_file_instance

    file_reader = get_file_reader("blah.h5")

    mock_h5py_file.assert_called_once_with("blah.h5")
    assert isinstance(file_reader, XspressMCAFileReader)


@patch("pyxspress.data.util.h5py.File")
def test_get_file_reader_returns_list_file_reader_if_no_mca_keys_present(
    mock_h5py_file,
) -> None:
    mock_file_instance = MagicMock()
    mock_file_instance.keys.return_value = [
        "ch0_time_frame",
        "ch0_time_stamp",
        "ch0_event_height",
        "ch0_reset_flag",
    ]
    mock_h5py_file.return_value = mock_file_instance

    file_reader = get_file_reader("blah.h5")

    mock_h5py_file.assert_called_once_with("blah.h5")
    assert isinstance(file_reader, XspressListFileReader)


@patch("pyxspress.data.util.h5py.File")
def test_get_file_reader_raises_FileNotFoundError_for_meta_file_no_matching_data(
    tmp_path,
) -> None:
    fake_meta_filename = f"{tmp_path}/fake_meta.h5"

    with raises(FileNotFoundError) as error:
        get_file_reader(fake_meta_filename)

    assert "No data files found" in str(error)


def test_get_file_reader_returns_mca_file_reader_for_example_mca_files_using_meta(
    example_mca_metadata_filepath,
) -> None:
    file_reader = get_file_reader(str(example_mca_metadata_filepath))

    assert isinstance(file_reader, XspressMCAFileReader)


def test_get_file_reader_returns_mca_file_reader_for_example_mca_files_using_A(
    example_mca_A_filepath,
) -> None:
    file_reader = get_file_reader(str(example_mca_A_filepath))

    assert isinstance(file_reader, XspressMCAFileReader)


def test_get_matching_xspress_files_returns_None_for_no_match(tmp_path) -> None:
    file_no_match = f"{tmp_path}/no_matching_files.h5"

    assert get_matching_xspress_files(file_no_match) == ([file_no_match], None)


def test_get_matching_xspress_files_returns_example_mca_files_using_meta_file(
    example_mca_metadata_filepath,
) -> None:
    metadata_filename = str(example_mca_metadata_filepath)
    example_directory = example_mca_metadata_filepath.parent

    data_files, metadata_file = get_matching_xspress_files(metadata_filename)

    assert metadata_file == f"{example_directory}/test-mca-1_meta.h5"
    assert data_files == [
        f"{example_directory}/test-mca-1_A_000000.h5",
        f"{example_directory}/test-mca-1_B_000000.h5",
        f"{example_directory}/test-mca-1_C_000000.h5",
        f"{example_directory}/test-mca-1_D_000000.h5",
    ]


def test_get_matching_xspress_files_returns_example_mca_files_using_A_file(
    example_mca_A_filepath,
) -> None:
    A_filename = str(example_mca_A_filepath)
    example_directory = example_mca_A_filepath.parent

    data_files, metadata_file = get_matching_xspress_files(A_filename)

    assert metadata_file == f"{example_directory}/test-mca-1_meta.h5"
    assert data_files == [
        f"{example_directory}/test-mca-1_A_000000.h5",
        f"{example_directory}/test-mca-1_B_000000.h5",
        f"{example_directory}/test-mca-1_C_000000.h5",
        f"{example_directory}/test-mca-1_D_000000.h5",
    ]
