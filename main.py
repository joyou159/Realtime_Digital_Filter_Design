from PyQt6 import QtWidgets, uic, QtGui
import numpy as np
import pyqtgraph as pg
import qdarkstyle
import sys
from scipy.signal import freqz, zpk2tf, dlti, TransferFunction


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_ui()
        self.init_complex_plane()
        self.plot_magnitude_and_phase()

    def init_ui(self):
        self.ui = uic.loadUi('Mainwindow.ui', self)
        self.setWindowTitle("Realtime Digital Filter Design")
        self.ui.correctPhase.clicked.connect(self.open_phase_correction_window)
        self.zPlane = self.ui.zPlane
        self.magPlot = self.ui.magPlot
        self.customSignal.clicked.connect(self.on_customSignal_cliked)
        self.importSignal.clicked.connect(self.on_importSignal_cliked)
        self.zerosButton.clicked.connect(self.on_zeros_cliked)
        self.polesButton.clicked.connect(self.on_poles_cliked)

    def on_customSignal_cliked(self):
        self.customSignal.setStyleSheet("background-color: red;")
        self.importSignal.setStyleSheet("")

    def on_importSignal_cliked(self):
        self.customSignal.setStyleSheet("")
        self.importSignal.setStyleSheet("background-color: red;")

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

        self.zeros = np.array([], dtype=complex)
        self.poles = np.array([0+0.90j], dtype=complex)

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
        w, mag, phase = self.get_the_mag_and_phase()

        # Plot the magnitude response
        self.magPlot.plotItem.showGrid(True, True)
        self.magPlot.clear()
        self.magPlot.plot(w, mag)
        self.magPlot.setLabel('left', 'Magnitude (dB)')
        self.magPlot.setLabel('bottom', 'Frequency (Hz)')

        # Plot the phase response
        self.phasePlot.plotItem.showGrid(True, True)
        self.phasePlot.clear()
        self.phasePlot.plot(w, phase)
        self.phasePlot.setLabel('left', 'Phase (radians)')
        self.phasePlot.setLabel('bottom', 'Frequency (Hz)')

    def calculate_points_on_circle(self):
        theta_for_half_circle = np.linspace(0, np.pi, 100)
        x_upper = np.cos(theta_for_half_circle)
        y_upper = np.sin(theta_for_half_circle)
        return x_upper + (y_upper * 1j)

    def open_phase_correction_window(self):
        # Disable interactivity in the main window
        self.setEnabled(False)
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

    def get_the_mag_and_phase(self):
        # Calculate frequency response
        w, h = freqz(np.poly(self.zeros), np.poly(self.poles))

        frequencies = w
        mag_response = np.abs(h)
        phase_response = np.angle(h)

        return frequencies, mag_response, phase_response


class PhaseCorrectionWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(PhaseCorrectionWindow, self).__init__(parent)
        uic.loadUi('phaseCorrection.ui', self)
        self.setWindowTitle("Phase Correction")
        self.destroyed.connect(self.on_window_closed)

    def on_window_closed(self):
        self.close()
        if self.parent():
            self.parent().setEnabled(True)


def main():
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
