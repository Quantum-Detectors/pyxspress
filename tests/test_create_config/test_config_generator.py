import difflib
from pathlib import Path
from unittest.mock import patch

from pyxspress.create_config.config_generator import ConfigGenerator


def test_generate_in_test_mode_generates_expected_files(tmp_path) -> None:
    num_cards = 4
    num_chans = 8
    mark = 2
    marker_channels = False
    odin_path = tmp_path
    epics_path = tmp_path
    test = True

    config_gen = ConfigGenerator(
        num_cards=num_cards,
        num_chans=num_chans,
        mark=mark,
        marker_channels=marker_channels,
        odin_path=odin_path,
        epics_path=epics_path,
        tcp_relay=False,
        test=test,
    )
    config_gen.clean()
    config_gen.generate()

    expected_dir = Path("test_files/config_8Ch")

    expected_files = {f.name for f in expected_dir.iterdir() if f.is_file()}
    generated_files = {f.name for f in odin_path.iterdir() if f.is_file()}

    # Ensure same set of files ---
    assert expected_files == generated_files, (
        f"Missing: {expected_files - generated_files}, "
        f"Extra: {generated_files - expected_files}"
    )

    # Ensure each file is identical
    def assert_files_equal(expected_file, generated_file):
        expected_text = expected_file.read_text().splitlines()
        generated_text = generated_file.read_text().splitlines()

        diff = list(
            difflib.unified_diff(
                expected_text,
                generated_text,
                fromfile=str(expected_file),
                tofile=str(generated_file),
                lineterm="",
            )
        )

        if diff:
            diff_output = "\n".join(diff)
            raise AssertionError(f"File mismatch: {expected_file.name}\n{diff_output}")

    for fname in expected_files:
        assert_files_equal(expected_dir / fname, odin_path / fname)


def test_generate_in_test_mode_markers_generates_expected_files(tmp_path) -> None:
    num_cards = 4
    num_chans = 8
    mark = 2
    marker_channels = True
    odin_path = tmp_path
    epics_path = tmp_path
    test = True

    config_gen = ConfigGenerator(
        num_cards=num_cards,
        num_chans=num_chans,
        mark=mark,
        marker_channels=marker_channels,
        odin_path=odin_path,
        epics_path=epics_path,
        tcp_relay=False,
        test=test,
    )
    config_gen.clean()
    config_gen.generate()

    expected_dir = Path("test_files/config_8Ch_marker")

    expected_files = {f.name for f in expected_dir.iterdir() if f.is_file()}
    generated_files = {f.name for f in odin_path.iterdir() if f.is_file()}

    # Ensure same set of files ---
    assert expected_files == generated_files, (
        f"Missing: {expected_files - generated_files}, "
        f"Extra: {generated_files - expected_files}"
    )

    # Ensure each file is identical
    def assert_files_equal(expected_file, generated_file):
        expected_text = expected_file.read_text().splitlines()
        generated_text = generated_file.read_text().splitlines()

        diff = list(
            difflib.unified_diff(
                expected_text,
                generated_text,
                fromfile=str(expected_file),
                tofile=str(generated_file),
                lineterm="",
            )
        )

        if diff:
            diff_output = "\n".join(diff)
            raise AssertionError(f"File mismatch: {expected_file.name}\n{diff_output}")

    for fname in expected_files:
        assert_files_equal(expected_dir / fname, odin_path / fname)


def test_generate_in_test_mode_with_tcp_relay_generates_expected_files(
    tmp_path,
) -> None:
    num_cards = 4
    num_chans = 8
    mark = 2
    marker_channels = False
    odin_path = tmp_path
    epics_path = tmp_path
    test = True

    config_gen = ConfigGenerator(
        num_cards=num_cards,
        num_chans=num_chans,
        mark=mark,
        marker_channels=marker_channels,
        odin_path=odin_path,
        epics_path=epics_path,
        tcp_relay=True,
        test=test,
    )
    config_gen.clean()
    config_gen.generate()

    expected_dir = Path("test_files/config_8Ch_tcp_relay")

    expected_files = {f.name for f in expected_dir.iterdir() if f.is_file()}
    generated_files = {f.name for f in odin_path.iterdir() if f.is_file()}

    # Ensure same set of files ---
    assert expected_files == generated_files, (
        f"Missing: {expected_files - generated_files}, "
        f"Extra: {generated_files - expected_files}"
    )

    # Ensure each file is identical
    def assert_files_equal(expected_file, generated_file):
        expected_text = expected_file.read_text().splitlines()
        generated_text = generated_file.read_text().splitlines()

        diff = list(
            difflib.unified_diff(
                expected_text,
                generated_text,
                fromfile=str(expected_file),
                tofile=str(generated_file),
                lineterm="",
            )
        )

        if diff:
            diff_output = "\n".join(diff)
            raise AssertionError(f"File mismatch: {expected_file.name}\n{diff_output}")

    for fname in expected_files:
        assert_files_equal(expected_dir / fname, odin_path / fname)


@patch("pyxspress.create_config.config_generator.rebuild_adodin")
def test_generate_rebuilds_adodin(mock_rebuild_adodin, tmp_path) -> None:
    num_cards = 4
    num_chans = 8
    mark = 2
    marker_channels = False
    odin_path = tmp_path
    epics_path = tmp_path
    test = False

    config_gen = ConfigGenerator(
        num_cards=num_cards,
        num_chans=num_chans,
        mark=mark,
        marker_channels=marker_channels,
        odin_path=odin_path,
        epics_path=epics_path,
        tcp_relay=False,
        test=test,
    )

    # Patch some of the paths in the same way the test flag sets them to
    # the test directory
    config_gen.adodin_ioc_boot_dir = tmp_path
    config_gen.adodin_edl_dir = tmp_path

    config_gen.clean()
    config_gen.generate()

    expected_dir = Path("test_files/config_8Ch")

    expected_files = {f.name for f in expected_dir.iterdir() if f.is_file()}
    generated_files = {f.name for f in odin_path.iterdir() if f.is_file()}

    # Ensure same set of files ---
    assert expected_files == generated_files, (
        f"Missing: {expected_files - generated_files}, "
        f"Extra: {generated_files - expected_files}"
    )

    # Ensure each file is identical
    def assert_files_equal(expected_file, generated_file):
        expected_text = expected_file.read_text().splitlines()
        generated_text = generated_file.read_text().splitlines()

        diff = list(
            difflib.unified_diff(
                expected_text,
                generated_text,
                fromfile=str(expected_file),
                tofile=str(generated_file),
                lineterm="",
            )
        )

        if diff:
            diff_output = "\n".join(diff)
            raise AssertionError(f"File mismatch: {expected_file.name}\n{diff_output}")

    for fname in expected_files:
        assert_files_equal(expected_dir / fname, odin_path / fname)

    # Check we requested ADOdin to be rebuilt
    mock_rebuild_adodin.assert_called_once_with(ConfigGenerator.adodin_dir)
