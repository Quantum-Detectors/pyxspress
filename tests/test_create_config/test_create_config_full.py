import difflib
from pathlib import Path

from pyxspress.create_config.config_generator import ConfigGenerator


def test_init(tmp_path):
    num_cards = 4
    num_chans = 8
    mark = 2
    odin_path = tmp_path
    epics_path = tmp_path
    test = True
    config_gen = ConfigGenerator(
        num_cards=num_cards,
        num_chans=num_chans,
        mark=mark,
        odin_path=odin_path,
        epics_path=epics_path,
        test=test
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

        diff = list(difflib.unified_diff(
            expected_text, generated_text,
            fromfile=str(expected_file),
            tofile=str(generated_file),
            lineterm=""
        ))

        if diff:
            diff_output = "\n".join(diff)
            raise AssertionError(f"File mismatch: {expected_file.name}\n{diff_output}")

    for fname in expected_files:
        assert_files_equal(expected_dir / fname, odin_path / fname)
