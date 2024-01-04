from PyQt6 import QtWidgets, uic, QtGui
import numpy as np
import pyqtgraph as pg
import qdarkstyle
import sys
from scipy.signal import freqz, zpk2tf, lfilter
import os
from scipy.io import wavfile
import csv
from Signal import Signal
from scipy.fft import fft
from PaddingArea import PaddingArea
from PyQt6.QtCore import Qt, QElapsedTimer
from PhaseCorrectionWindow import PhaseCorrectionWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_ui()
        self.init_complex_plane()
        self.plot_magnitude_and_phase()
        self.zPlane = self.ui.zPlane
        self.magPlot = self.ui.magPlot
        self.input_signal = None
        self.input_mode = None
        self.point_per_second = 1  # Initial filter speed
        self.idx = 0
        self.signal = Signal()
        self.phase_correction_filters = []
        self.zeros_all_pass = np.array([], dtype=complex)
        self.poles_all_pass = np.array([], dtype=complex)

    def init_ui(self):
        self.ui = uic.loadUi('Mainwindow.ui', self)
        self.setWindowTitle("Realtime Digital Filter Design")
        # Plot the magnitude response
        self.inputSignal.plotItem.showGrid(True, True)
        self.inputSignal.clear()
        self.inputSignal.setLabel('left', 'Magnitude')
        self.inputSignal.setLabel('bottom', 'Time')
        # Plot the magnitude response
        self.outputSignal.plotItem.showGrid(True, True)
        self.outputSignal.clear()
        self.outputSignal.setLabel('left', 'Magnitude')
        self.outputSignal.setLabel('bottom', 'Time')

        # Plot the magnitude response
        self.magPlot.plotItem.showGrid(True, True)

        self.magPlot.setLabel('left', 'Magnitude (dB)')
        self.magPlot.setLabel('bottom', 'Frequency (Hz)')

        # Plot the phase response
        self.phasePlot.plotItem.showGrid(True, True)

        self.phasePlot.setLabel('left', 'Phase (radians)')
        self.phasePlot.setLabel('bottom', 'Frequency (Hz)')

        self.ui.correctPhase.clicked.connect(self.open_phase_correction_window)
        self.importSignal.clicked.connect(self.on_importSignal_cliked)
        self.zerosButton.clicked.connect(self.on_zeros_cliked)
        self.polesButton.clicked.connect(self.on_poles_cliked)
        self.customSignal.clicked.connect(self.on_customSignal_cliked)
        self.Speed.setMinimum(1)
        self.Speed.setMaximum(100)
        self.Speed.setValue(1)  # Initial value
        self.Speed.valueChanged.connect(self.update_filter_speed)
        self.padding_area = PaddingArea(self)
        self.area.layout().addWidget(self.padding_area)

    def update_filter_speed(self, value):
        self.point_per_second = value
        self.numOfPoints.setText(f"{self.point_per_second} points/sec")

    def update_filter(self):
        if self.idx < len(self.signal.output_signal_after_filter):
            self.idx += self.point_per_second

        # Plot updated output signal
        self.outputSignal.plot(
            self.signal.time[:self.idx], self.signal.output_signal_after_filter[:self.idx], pen='r')

        self.inputSignal.plot(
            self.signal.time[:self.idx], self.signal.data[:self.idx], pen='b')

    def on_importSignal_cliked(self):
        self.input_mode = "import"
        self.browse()

    def on_customSignal_cliked(self):
        if self.input_mode == "custom":
            self.input_mode = None
            self.padding_area.elapsed_timer = QElapsedTimer()
            self.padding_area.first_time = True
        else:
            self.input_mode = "custom"
        # Toggle button color between red and white
        current_color = self.sender().styleSheet()
        if 'background-color: red' in current_color:
            self.sender().setStyleSheet("")
        else:
            self.sender().setStyleSheet("background-color: red;")

    def browse(self):
        self.idx = 0
        file_filter = "Raw Data (*.csv *.wav)"
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Open Signal File', './', filter=file_filter)

        if file_path:
            file_name = os.path.basename(file_path)
            self.open_file(file_path, file_name)

    def open_file(self, path: str, file_name: str):
        # Lists to store time and data
        time = []  # List to store time values
        data = []  # List to store data values
        frequency = 0

        # Extract the file extension (last 3 characters) from the path
        filetype = path[-3:]

        if filetype == "wav":
            # Read the WAV file
            sample_rate, data = wavfile.read(path)
            time = np.linspace(0, data.shape[0] / sample_rate, data.shape[0])

        # Check if the file type is CSV, text (txt), or Excel (xls)
        if filetype in ["csv", "txt", "xls"]:
            # Open the data file for reading ('r' mode)
            with open(path, 'r') as data_file:
                # Create a CSV reader object with a comma as the delimiter
                data_reader = csv.reader(data_file, delimiter=',')
                next(data_reader)

                # Iterate through each row (line) in the data file
                for row in data_reader:

                    # Extract the time value from the first column (index 0)
                    time_value = float(row[0])

                    # Extract the amplitude value from the second column (index 1)
                    amplitude_value = float(row[1])

                    # Append the time and amplitude values to respective lists
                    time.append(time_value)
                    data.append(amplitude_value)

        # Create a Signal object with the file name without the extension
        self.signal.data = data
        self.signal.time = time

        self.plot_input_and_output_signal()

    def on_zeros_cliked(self):
        self.zerosButton.setStyleSheet("background-color: red;")
        self.polesButton.setStyleSheet("")

    def on_poles_cliked(self):
        self.zerosButton.setStyleSheet("")
        self.polesButton.setStyleSheet("background-color: red;")

    def init_complex_plane(self):
        # Create a PyQtGraph window for the complex plane
        self.ui.zPlane.clear()

        self.zPlane.plotItem.showGrid(True, True)
        self.plot_unit_circle()

        self.zeros = np.array([-1+0j], dtype=complex)
        self.poles = np.array([], dtype=complex)

        if self.zeros.size > 0:
            self.plot_complex_points(
                self.zeros, color='r', symbol='o', size=10)
        if self.poles.size > 0:
            self.plot_complex_points(
                self.poles, color='b', symbol='x', size=12)

    def plot_unit_circle(self):
        # Create an array of angles from 0 to 2*pi
        theta = np.linspace(0, 2 * np.pi, 100)
        # Parametric equations for the unit circle
        x = np.cos(theta)
        y = np.sin(theta)
        # Plot the circle
        self.zPlane.plot(x, y)

    def plot_complex_points(self, points, color, symbol, size):
        self.zPlane.scatterPlot([points.real], [points.imag], pen=color,
                                symbol=symbol, symbolPen=color, symbolSize=size, symbolBrush=color)

    def plot_magnitude_and_phase(self):
        self.points_on_the_circle = self.calculate_points_on_circle()
        w, mag, phase = self.get_the_mag_and_phase(self.zeros, self.poles)
        self.magPlot.clear()
        self.magPlot.plot(w, mag)
        self.phasePlot.clear()
        self.phasePlot.plot(w, phase)

    def plot_input_and_output_signal(self):
        numerator, denominator = zpk2tf(self.zeros, self.poles, 1)
        self.signal.output_signal_after_filter = np.real(
            lfilter(numerator, denominator, self.signal.data))

        # Timer to update filter
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_filter)
        self.timer.start(1000)  # Update every 10 milliseconds

    def calculate_points_on_circle(self):
        theta_for_half_circle = np.linspace(0, np.pi, 100)
        x_upper = np.cos(theta_for_half_circle)
        y_upper = np.sin(theta_for_half_circle)
        return x_upper + (y_upper * 1j)

    def open_phase_correction_window(self):
        # Open a new window
        new_window = PhaseCorrectionWindow(self)
        new_window.show()

    def show_error_message(self, message):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()

    def closeEvent(self, event):
        self.setEnabled(True)
        super(MainWindow, self).closeEvent(event)

    def get_the_mag_and_phase(self, zeros, poles):
        # Calculate frequency response
        w, h = freqz(np.poly(zeros), np.poly(poles))

        frequencies = w
        mag_response = np.abs(h)
        phase_response = np.angle(h)

        return frequencies, mag_response, phase_response


def main():
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
