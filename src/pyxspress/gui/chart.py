"""
Chart widget

Used to display line charts
"""

import numpy
from PySide6.QtCharts import QAbstractAxis, QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPainter

from pyxspress.util import Loggable


class LineChartWidget(QChartView, Loggable):
    def __init__(
        self,
        title: str | None = None,
    ):
        """Create a line chart widget to display data

        Expects a 1D array of data for a single line series or 2D array of
        multiple line series

        Based on the Qt chart view widget

        Args:
            title (Optional[str]): Title of chart (optional)
        """
        super().__init__()

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRubberBand(QChartView.RubberBand.RectangleRubberBand)

        # Chart to hold the series data
        self.data_chart = QChart()
        self.setChart(self.data_chart)
        self.data_chart.legend().hide()

        # Store reference to y axis
        self.y_axis: QAbstractAxis = QValueAxis()

        # Series data properties
        self.series: list[QLineSeries] = []
        self.series_names: list[str] = []
        self.series_length: int = 0
        self.x_values: numpy.ndarray = numpy.array([])
        self.max_y_value = 0.0

        if title is not None:
            self.data_chart.setTitle(title)

        self.logger.debug(f"Created chart: (title: {title})")

    def set_series_names(self, names: list[str]):
        self.series_names = names

    @Slot(numpy.ndarray)
    def update_chart(self, data: numpy.ndarray):
        """Update the chart with the input data.

        - Input data should be 1D or 2D
        - If 2D then the first dimension should be series number

        Args:
            data (numpy.ndarray): Input data
        """
        if data.ndim > 2:
            self.logger.error(f"Only 1D or 2D data supported. Got {data.ndim}")
            return

        elif data.ndim == 1:
            # Reshape 1D to 2D so we can use same logic block for plotting
            data = data.reshape((1, data.shape[0]))

        num_series = data.shape[0]
        series_length = data.shape[1]

        # Check if we can re-use existing series and replace the data
        if num_series == len(self.series) and series_length == self.series_length:
            # Replace the data
            for series_index in range(num_series):
                self.series[series_index].replaceNp(
                    self.x_values,  # type: ignore
                    data[series_index, :].astype(numpy.float32),  # type: ignore
                )

            # Check for Y axis rescaling
            max_y_value = max(numpy.max(data), 1.0)
            if max_y_value > self.max_y_value or max_y_value < 0.5 * self.max_y_value:
                self.y_axis.setRange(0.0, 1.05 * max_y_value)
                self.max_y_value = max_y_value

        # Need to create new series and axes
        else:
            # Common attributes
            self.x_values = numpy.arange(data.shape[1], dtype=numpy.float32)
            self.max_y_value = max(numpy.max(data), 1.0)
            self.series_length = series_length

            # Delete and recreate each series
            self.data_chart.removeAllSeries()
            self.series = []
            for series_index in range(num_series):
                self.series.append(QLineSeries())
                self.series[series_index].appendNp(
                    self.x_values,  # type: ignore
                    data[series_index, :].astype(numpy.float32),  # type: ignore
                )
                self.data_chart.addSeries(self.series[series_index])

            # Set up chart axes
            self.data_chart.createDefaultAxes()
            x_axis = self.data_chart.axes(Qt.Orientation.Horizontal)[0]
            x_axis.setLabelFormat("%i")  # type: ignore

            self.y_axis = self.data_chart.axes(Qt.Orientation.Vertical)[0]
            self.y_axis.setLabelFormat("%i")  # type: ignore
            self.y_axis.setRange(0.0, 1.05 * self.max_y_value)

            # Legend
            if len(self.series) == len(self.series_names):
                self.data_chart.legend().show()
                for series_index in range(num_series):
                    self.series[series_index].setName(self.series_names[series_index])
            else:
                self.data_chart.legend().hide()
