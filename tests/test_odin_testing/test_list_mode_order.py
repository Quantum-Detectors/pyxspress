from unittest.mock import call, patch

from pyxspress.data.xspress_list_file_reader import ListDataset, XspressListFileReader
from pyxspress.odin_testing import check_time_frame_ordering, check_time_stamp_ordering


def test_time_stamp_ordering_returns_True_for_success() -> None:
    file_reader = XspressListFileReader()
    file_reader.channels = [0, 1, 2, 3]

    time_stamps_in_order = range(1000)

    with patch.object(file_reader, "get_channel_dataset") as mock_get_channel_dataset:
        mock_get_channel_dataset.return_value = time_stamps_in_order

        assert check_time_stamp_ordering(file_reader) is True

        mock_get_channel_dataset.assert_has_calls(
            [
                call(0, ListDataset.TimeStamp),
                call(1, ListDataset.TimeStamp),
                call(2, ListDataset.TimeStamp),
                call(3, ListDataset.TimeStamp),
            ]
        )


def test_time_stamp_ordering_returns_True_for_success_single_channel() -> None:
    file_reader = XspressListFileReader()
    file_reader.channels = [0, 1, 2, 3]

    time_stamps_in_order = range(1000)

    with patch.object(file_reader, "get_channel_dataset") as mock_get_channel_dataset:
        mock_get_channel_dataset.return_value = time_stamps_in_order

        assert check_time_stamp_ordering(file_reader, channel=2) is True

        mock_get_channel_dataset.assert_called_once_with(2, ListDataset.TimeStamp)


def test_time_stamp_ordering_returns_False_for_failure() -> None:
    file_reader = XspressListFileReader()
    file_reader.channels = [0, 1, 2, 3]

    time_stamps_out_of_order = [1, 2, -1, 3, 4, 5, 10]

    with patch.object(file_reader, "get_channel_dataset") as mock_get_channel_dataset:
        mock_get_channel_dataset.return_value = time_stamps_out_of_order

        assert check_time_stamp_ordering(file_reader) is False

        mock_get_channel_dataset.assert_has_calls(
            [
                call(0, ListDataset.TimeStamp),
                call(1, ListDataset.TimeStamp),
                call(2, ListDataset.TimeStamp),
                call(3, ListDataset.TimeStamp),
            ]
        )


def test_time_frame_ordering_returns_True_for_success() -> None:
    file_reader = XspressListFileReader()
    file_reader.channels = [0, 1, 2, 3]

    time_frames_in_order = range(1000)

    with patch.object(file_reader, "get_channel_dataset") as mock_get_channel_dataset:
        mock_get_channel_dataset.return_value = time_frames_in_order

        assert check_time_frame_ordering(file_reader) is True

        mock_get_channel_dataset.assert_has_calls(
            [
                call(0, ListDataset.TimeFrame),
                call(1, ListDataset.TimeFrame),
                call(2, ListDataset.TimeFrame),
                call(3, ListDataset.TimeFrame),
            ]
        )


def test_time_frame_ordering_returns_True_for_success_single_channel() -> None:
    file_reader = XspressListFileReader()
    file_reader.channels = [0, 1, 2, 3]

    time_frames_in_order = range(1000)

    with patch.object(file_reader, "get_channel_dataset") as mock_get_channel_dataset:
        mock_get_channel_dataset.return_value = time_frames_in_order

        assert check_time_frame_ordering(file_reader, channel=2) is True

        mock_get_channel_dataset.assert_called_once_with(2, ListDataset.TimeFrame)


def test_time_frame_ordering_returns_False_for_failure() -> None:
    file_reader = XspressListFileReader()
    file_reader.channels = [0, 1, 2, 3]

    time_frames_out_of_order = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, -3, 3, 3, 4]

    with patch.object(file_reader, "get_channel_dataset") as mock_get_channel_dataset:
        mock_get_channel_dataset.return_value = time_frames_out_of_order

        assert check_time_frame_ordering(file_reader) is False

        mock_get_channel_dataset.assert_has_calls(
            [
                call(0, ListDataset.TimeFrame),
                call(1, ListDataset.TimeFrame),
                call(2, ListDataset.TimeFrame),
                call(3, ListDataset.TimeFrame),
            ]
        )
