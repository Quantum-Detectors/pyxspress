"""
Main window

The main window of the application
"""

import glob
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyxspress import __version__
from pyxspress.data import FileReaderInterface, get_file_reader
from pyxspress.gui import LineChartWidget
from pyxspress.gui.util import get_image_path
from pyxspress.util import Loggable

xspress_scalers = {
    0: "Time",
    1: "Reset ticks",
    2: "Reset count",
    3: "All event",
    4: "All good",
    5: "In win 0",
    6: "In win 1",
    7: "Pile up",
    8: "Total time",
}


class MainWindow(QMainWindow, Loggable):
    minimum_width = 1440

    header_height = 64
    footer_height = 32
    default_margin = 5
    default_widget_spacing = 5
    version_widget_width = 100
    data_viewer_height = 600

    def __init__(self) -> None:
        """Create the main window"""
        super().__init__()

        self.file_reader: FileReaderInterface
        self.chart_widgets: dict[int, LineChartWidget] = {}
        self.default_file_path_text = "Select Xspress HDF5 file..."
        self.last_success_file_path_text = ""

        self.channel_enable_checkboxes: dict[int, QCheckBox] = {}
        self.enabled_channels: list[int] = []

        self.scalar_value_checkboxes: list[QLabel] = []

        # Create the child UI components
        self._setup_core_ui()

        self.logger.debug("Main window initialised")

    def _setup_core_ui(self) -> None:
        """Called to create the child UI components"""
        self.setWindowTitle("Xspress Odin data viewer")
        self.setMinimumWidth(self.minimum_width)

        # Central widget for the entire window
        self.core_widget = QFrame()
        self.core_widget.setObjectName("CoreWidget")
        self.core_widget.setStyleSheet("#CoreWidget {background-color:white;}")
        self.core_layout = QVBoxLayout()
        self.core_layout.setContentsMargins(0, 0, 0, 0)
        self.core_layout.setSpacing(0)
        self.core_widget.setLayout(self.core_layout)
        self.setCentralWidget(self.core_widget)

        # The central widget layout is split into multiple child layouts
        self.header_layout = QHBoxLayout()
        self.contents_layout = QGridLayout()
        self.footer_layout = QHBoxLayout()
        self.core_layout.addLayout(self.header_layout)
        self.core_layout.addLayout(self.contents_layout)
        self.core_layout.addLayout(self.footer_layout)

        # Header frame
        header_frame = QFrame()
        header_frame.setFixedHeight(self.header_height)
        # Set fill colour to QD blue
        header_frame.setObjectName("TitleWidget")
        header_frame.setStyleSheet("#TitleWidget {background-color:#0069b4;}")
        header_frame_layout = QHBoxLayout()
        header_frame_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_frame_layout.setContentsMargins(0, 0, self.default_margin, 0)
        header_frame.setLayout(header_frame_layout)
        self.header_layout.addWidget(header_frame)

        # Contents layout to hold the main UI components
        self.contents_layout.setContentsMargins(
            self.default_margin,
            self.default_margin,
            self.default_margin,
            self.default_margin,
        )
        self.contents_layout.setSpacing(self.default_widget_spacing)

        # Data navigation on bottom left
        self.data_navigation = QGroupBox("Navigation")
        self.navigation_layout = QGridLayout()
        self.navigation_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.data_navigation.setLayout(self.navigation_layout)
        self.contents_layout.addWidget(self.data_navigation, 1, 0)
        self.__setup_navigation_widget()

        # Scalars on bottom right
        self.scalar_box = QGroupBox("Scalars")
        self.scalar_box_layout = QGridLayout()
        self.scalar_box_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scalar_box_layout.setContentsMargins(
            self.default_margin,
            self.default_margin,
            self.default_margin,
            self.default_margin,
        )
        self.scalar_box.setLayout(self.scalar_box_layout)
        self.contents_layout.addWidget(self.scalar_box, 1, 1)
        self.__setup_scalar_data_widget()

        # Data viewer on top
        self.__setup_charts()

        # Footer frame
        footer_frame = QFrame()
        footer_frame.setFixedHeight(self.footer_height)
        # Set fill colour to QD atom blue
        footer_frame.setObjectName("FooterWidget")
        footer_frame.setStyleSheet("#FooterWidget {background-color:#009fe3;}")
        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight
        )
        footer_layout.setContentsMargins(
            self.default_widget_spacing,
            0,
            2 * self.default_widget_spacing,
            2 * self.default_widget_spacing,
        )
        footer_frame.setLayout(footer_layout)
        self.footer_layout.addWidget(footer_frame)

        # Add QD logo to header frame
        qd_logo_image = QPixmap(get_image_path("QD_logo_white.png"))
        qd_logo_image_widget = QLabel()
        qd_logo_image_widget.setPixmap(qd_logo_image)
        qd_logo_image_widget.setFixedHeight(self.header_height)
        header_frame_layout.addWidget(qd_logo_image_widget)

        # Add version number to footer
        version_widget = QLabel(f"Version {__version__}")
        version_widget.setStyleSheet(
            "font-weight: bold; font-size: 8pt; color: white; text-align: right;"
        )
        footer_layout.addWidget(version_widget)

        # Now display the main window!
        self.show()

    def __setup_navigation_widget(self):
        """Set up the navigation widget and child widgets"""
        # File browser
        file_path_label = QLabel("File path")
        self.file_path_line_edit = QLineEdit()
        self.file_path_line_edit.setText(self.default_file_path_text)
        self.file_path_line_edit.editingFinished.connect(
            self.__manual_file_path_callback
        )
        file_path_browse_button = QPushButton("Browse")
        file_path_browse_button.setMaximumWidth(80)
        file_path_browse_button.clicked.connect(self.__file_browse_callback)
        file_path_value_box = QWidget()
        file_path_value_layout = QHBoxLayout()
        file_path_value_layout.setContentsMargins(0, 0, 0, 0)
        file_path_value_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        file_path_value_box.setLayout(file_path_value_layout)
        file_path_value_layout.addWidget(self.file_path_line_edit)
        file_path_value_layout.addWidget(file_path_browse_button)

        self.navigation_layout.addWidget(file_path_label, 0, 0)
        self.navigation_layout.addWidget(file_path_value_box, 0, 1)

        # Combined plot checkbox
        combined_plot_label = QLabel("Combined plot")
        self.combined_plot_checkbox = QCheckBox()
        self.combined_plot_checkbox.checkStateChanged.connect(
            self.__combined_plot_checkbox_changed
        )

        self.navigation_layout.addWidget(combined_plot_label, 1, 0)
        self.navigation_layout.addWidget(self.combined_plot_checkbox, 1, 1)

        # Frame browser buttons
        frame_number_label = QLabel("Frame number")
        skip_to_start_frame_button = QPushButton("|<")
        skip_to_start_frame_button.setFixedWidth(50)
        previous_frame_button = QPushButton("<")
        previous_frame_button.setFixedWidth(50)
        self.frame_number = QLineEdit()
        self.frame_number.setText("0")
        self.frame_number.setMaximumWidth(90)
        self.total_frames_in_file = QLabel("/ 0")
        self.total_frames_in_file.setMaximumWidth(90)
        next_frame_button = QPushButton(">")
        next_frame_button.setFixedWidth(50)
        skip_to_end_frame_button = QPushButton(">|")
        skip_to_end_frame_button.setFixedWidth(50)

        skip_to_start_frame_button.clicked.connect(self.__skip_to_start_callback)
        previous_frame_button.clicked.connect(self.__previous_frame_callback)
        self.frame_number.editingFinished.connect(self.__set_frame_number_callback)
        next_frame_button.clicked.connect(self.__next_frame_callback)
        skip_to_end_frame_button.clicked.connect(self.__skip_to_end_callback)

        frame_navigation_widget = QWidget()
        frame_navigation_layout = QHBoxLayout()
        frame_navigation_widget.setLayout(frame_navigation_layout)
        frame_navigation_layout.setContentsMargins(0, 0, 0, 0)
        frame_navigation_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        frame_navigation_layout.addWidget(skip_to_start_frame_button)
        frame_navigation_layout.addWidget(previous_frame_button)
        frame_navigation_layout.addWidget(self.frame_number)
        frame_navigation_layout.addWidget(self.total_frames_in_file)
        frame_navigation_layout.addWidget(next_frame_button)
        frame_navigation_layout.addWidget(skip_to_end_frame_button)

        self.navigation_layout.addWidget(frame_number_label, 2, 0)
        self.navigation_layout.addWidget(frame_navigation_widget, 2, 1)

        # Number of channels
        num_channels_label = QLabel("Num channels")
        self.num_channels = QLabel("")

        self.navigation_layout.addWidget(num_channels_label, 3, 0)
        self.navigation_layout.addWidget(self.num_channels, 3, 1)

        # Enabled channels
        enabled_channels_label = QLabel("Enabled channels")

        self.enabled_channels_row = 4
        self.maxumum_channels_per_row = 16
        enabled_channels_box = QWidget()
        self.enabled_channels_layout = QGridLayout()
        enabled_channels_box.setLayout(self.enabled_channels_layout)
        self.enabled_channels_layout.setContentsMargins(0, 0, 0, 0)
        self.enabled_channels_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.navigation_layout.addWidget(
            enabled_channels_label, self.enabled_channels_row, 0
        )
        self.navigation_layout.addWidget(
            enabled_channels_box, self.enabled_channels_row, 1
        )

    def __setup_scalar_data_widget(self):
        # Delete any existing value widgets
        for widget_number in range(len(self.scalar_value_checkboxes)):
            self.scalar_value_checkboxes[widget_number].setParent(None)
            self.scalar_box_layout.removeWidget(
                self.scalar_value_checkboxes[widget_number]
            )

        # Channel number
        channel_label = QLabel("Channel")
        channel_label.setMinimumWidth(100)
        self.scalar_box_layout.addWidget(channel_label, 0, 0)

        # Scalar titles
        row = 1
        for scaler in xspress_scalers:
            scaler_label = QLabel(xspress_scalers[scaler])
            scaler_label.setMinimumWidth(100)
            self.scalar_box_layout.addWidget(scaler_label, row, 0)
            row += 1

        if len(self.enabled_channels) == 0:
            # Placeholder values
            channel_value = QLabel("0")
            self.scalar_value_checkboxes.append(channel_value)
            self.scalar_box_layout.addWidget(channel_value, 0, 1)

            for row in range(9):
                scalar_value = QLabel("0.0")
                self.scalar_value_checkboxes.append(scalar_value)
                self.scalar_box_layout.addWidget(scalar_value, row + 1, 1)

        else:
            # Track by column index in case some channels are disabled
            column_index = 1
            for channel in self.enabled_channels:
                channel_value_label = QLabel(f"{channel}")
                channel_value_label.setMinimumWidth(100)
                self.scalar_value_checkboxes.append(channel_value_label)
                self.scalar_box_layout.addWidget(channel_value_label, 0, column_index)

                for scalar in range(9):
                    value_label = QLabel("0.0")
                    self.scalar_value_checkboxes.append(value_label)
                    self.scalar_box_layout.addWidget(
                        value_label, scalar + 1, column_index
                    )

                column_index += 1

    def __skip_to_start_callback(self):
        if self.file_reader.open:
            self.__show_frame(1)
            self.frame_number.setText("1")

    def __skip_to_end_callback(self):
        if self.file_reader.open:
            self.__show_frame(self.file_reader.num_frames)
            self.frame_number.setText(f"{self.file_reader.num_frames}")

    def __previous_frame_callback(self):
        if self.file_reader.open:
            requested_frame_number = int(self.frame_number.text()) - 1
            if requested_frame_number > 0:
                self.__show_frame(requested_frame_number)
                self.frame_number.setText(f"{requested_frame_number}")

    def __next_frame_callback(self):
        if self.file_reader.open:
            requested_frame_number = int(self.frame_number.text()) + 1
            if requested_frame_number <= self.file_reader.num_frames:
                self.__show_frame(requested_frame_number)
                self.frame_number.setText(f"{requested_frame_number}")

    def __set_frame_number_callback(self):
        """Callback from frame number QLineEdit to manually specify frame number"""
        if self.file_reader.open:
            requested_frame_number = int(self.frame_number.text())
            if (
                requested_frame_number > 0
                and requested_frame_number <= self.file_reader.num_frames
            ):
                self.__show_frame(requested_frame_number)

    def __file_browse_callback(self):
        """Callback from selecting a file using the browse button"""
        self.logger.debug("Opening file browser")
        file_name = QFileDialog().getOpenFileName(
            filter="Xspress HDF5 file (*.h5);; All files (*.*)"
        )[0]
        if len(file_name) > 0:
            self.logger.info(f"Opening {file_name}")
            self.__open_xspress_file(file_name)

    def __manual_file_path_callback(self):
        """Callback from manually editing the file path to open"""
        text = self.file_path_line_edit.text()
        if text != self.default_file_path_text and len(text) > 0:
            self.logger.info(f"Opening {text}")
            self.__open_xspress_file(text)

    def __open_xspress_file(self, file_name: str):
        """Open the Xspress HDF5 file(s)

        The companion file (i.e. _A and _B files) will be opened if the file
        name has the correct file name pattern and the _B file exists.

        Args:
            file_name (str): File name of Xspress HDF5 file
        """
        # Create our file reader
        self.file_reader = get_file_reader(file_name)

        # Get companion HDF5 files if we have pattern
        suffix_pattern = "_000000.h5"
        meta_file: str | None = None
        if suffix_pattern in file_name:
            # Channel files
            file_prefix = file_name.split(suffix_pattern)[0][:-1]
            file_pattern = f"{file_prefix}*{suffix_pattern}"
            self.logger.info(f"Looking for files matching pattern: {file_pattern}")
            file_list = sorted(glob.glob(file_pattern))
            self.logger.info(f"Found files: {file_list}")
            assert len(file_list) > 0, "Did not find matching files"

            # Metadata file
            meta_file_name = f"{file_prefix}meta.h5"
            if os.path.exists(meta_file_name):
                self.logger.info(f"Found metadata file: {meta_file_name}")
                meta_file = meta_file_name

        else:
            file_list = [file_name]

        if self.file_reader.open_files(file_list, meta_file):
            self.total_frames_in_file.setText(f" / {self.file_reader.num_frames}")
            self.num_channels.setText(f"{self.file_reader.num_channels}")

            self.__setup_enable_channel_checkboxes()
            self.__setup_charts()
            self.__setup_scalar_data_widget()

            self.frame_number.setText("1")
            self.frame_number.setValidator(
                QIntValidator(1, self.file_reader.num_frames)
            )
            self.__show_frame(1)

            self.file_path_line_edit.setText(file_name)
            self.last_success_file_path_text = file_name

        else:
            self.file_path_line_edit.setText(self.last_success_file_path_text)

    def __setup_enable_channel_checkboxes(self) -> None:
        """Set up the enable channel checkboxes to allow the user to disable/enable
        viewing of each channel
        """
        # Clear existing checkboxes
        if len(self.channel_enable_checkboxes) > 1:
            for ch in self.channel_enable_checkboxes:
                self.channel_enable_checkboxes[ch].setParent(None)

        self.channel_enable_checkboxes = {}

        # Add new checkboxes
        row = 0
        col = 0
        for ch in self.file_reader.channels:
            checkbox = QCheckBox(f"Ch{ch}")
            checkbox.setFixedWidth(50)
            checkbox.setCheckState(Qt.CheckState.Checked)
            checkbox.stateChanged.connect(self.__enable_channel_checkbox_callback)
            self.channel_enable_checkboxes[ch] = checkbox
            self.enabled_channels_layout.addWidget(checkbox, row, col)

            # Increment column or row
            col += 1
            if col > self.maxumum_channels_per_row - 1:
                col = 0
                row += 1

        # All channels enabled by default
        self.enabled_channels = self.file_reader.channels

    def __enable_channel_checkbox_callback(self, _: Qt.CheckState) -> None:
        """Called whenever an enable channel checkbox is updated

        Args:
            _ (Qt.CheckState): New state
        """
        self.enabled_channels = [
            ch
            for ch in self.channel_enable_checkboxes
            if self.channel_enable_checkboxes[ch].checkState() is Qt.CheckState.Checked
        ]

        self.logger.debug(f"Got enabled channels: {self.enabled_channels}")
        self.__setup_charts()
        self.__setup_scalar_data_widget()
        self.__show_frame(int(self.frame_number.text()))

    def __combined_plot_checkbox_changed(self, _: Qt.CheckState):
        """Callback for the combined plot checkbox when the state is changed

        Args:
            _ (Qt.CheckState): New state
        """
        if self.file_reader.open:
            self.__setup_charts()
            self.__show_frame(int(self.frame_number.text()))

    def __setup_charts(self):
        """Create the chart(s) to display the data"""
        if len(self.chart_widgets) > 0:
            # Clear out the existing viewer widget(s)
            for channel in self.chart_widgets:
                self.data_viewer_layout.removeWidget(self.chart_widgets[channel])
                self.chart_widgets[channel].setParent(None)

            self.contents_layout.removeWidget(self.data_viewer)
            self.data_viewer.setParent(None)

        # Create the viewer widget
        self.data_viewer = QWidget()
        self.data_viewer_layout = QGridLayout()
        self.data_viewer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.data_viewer.setLayout(self.data_viewer_layout)
        self.data_viewer.setContentsMargins(
            self.default_margin,
            self.default_margin,
            self.default_margin,
            self.default_margin,
        )
        self.data_viewer.setMinimumHeight(self.data_viewer_height)
        self.contents_layout.addWidget(self.data_viewer, 0, 0, 1, 2)

        self.chart_widgets = {}

        combined_plot = (
            self.combined_plot_checkbox.checkState() is Qt.CheckState.Checked
        )
        if combined_plot:
            self.chart_widgets[-1] = LineChartWidget()
            self.chart_widgets[-1].setMinimumWidth(
                self.width() - 4 * self.default_margin
            )
            self.chart_widgets[-1].setMinimumHeight(
                self.data_viewer_height - 4 * self.default_margin
            )
            self.data_viewer_layout.addWidget(
                self.chart_widgets[-1],
                0,
                0,
                alignment=Qt.AlignmentFlag.AlignCenter,
            )
            self.chart_widgets[-1].series_names = [
                f"Ch {ch}" for ch in self.enabled_channels
            ]
        else:
            charts_per_row = 4
            row = 0
            col = 0
            for channel in self.enabled_channels:
                self.chart_widgets[channel] = LineChartWidget(title=f"Ch {channel}")
                self.data_viewer_layout.addWidget(
                    self.chart_widgets[channel],
                    row,
                    col,
                    alignment=Qt.AlignmentFlag.AlignCenter,
                )

                # Update position
                col += 1
                if col >= charts_per_row:
                    col = 0
                    row += 1

    def __show_frame(self, frame_number: int):
        """Update the shown frame number

        This is 1-indexed (i.e. first frame is 1)

        Args:
            frame_number (int): Frame number to display
        """
        # Check we have some enabled channels
        if len(self.enabled_channels) == 0:
            self.logger.warning("No channels enabled")
            return

        self.logger.debug(f"Showing frame {frame_number}")

        if self.combined_plot_checkbox.checkState() is Qt.CheckState.Checked:
            self.chart_widgets[-1].update_chart(
                self.file_reader.get_channel_data(
                    self.enabled_channels, frame_number - 1
                )
            )

        else:
            for channel in self.enabled_channels:
                self.chart_widgets[channel].update_chart(
                    self.file_reader.get_channel_data(channel, frame_number - 1)
                )

        self.__update_scalar_values(frame_number)

    def __update_scalar_values(self, frame_number: int):
        scalar_data = self.file_reader.get_scalar_data(
            self.enabled_channels, frame_number - 1
        )

        if scalar_data is None:
            return
        elif scalar_data.ndim == 1:
            # Reshape so we can "loop" over the channel
            scalar_data.resize((1, scalar_data.shape[0]))

        # Track channel index instead of channel number in case some are disabled
        channel_index = 0
        for _ in self.enabled_channels:
            for scalar_num in range(len(xspress_scalers)):
                item = self.scalar_box_layout.itemAtPosition(
                    scalar_num + 1, channel_index + 1
                )
                if item:
                    widget = item.widget()
                    assert isinstance(widget, QLabel)
                    widget.setText(f"{scalar_data[channel_index, scalar_num]}")

            channel_index += 1
