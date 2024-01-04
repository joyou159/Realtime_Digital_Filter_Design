from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtCore import QTimer
import numpy as np
import pyqtgraph as pg
import qdarkstyle
import sys
from UnitCircle import UnitCircle


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi('Mainwindow.ui', self)
        self.setWindowTitle("Realtime Digital Filter Design")
        self.ui.correctPhase.clicked.connect(self.open_phase_correction_window)
        self.zPlane = self.ui.zPlane
        self.magPlot = self.ui.magPlot

        self.circle_object = UnitCircle(self.ui)

    def init_complex_plane(self):
        # Create a PyQtGraph window for the complex plane
        self.ui.zPlane.clear()

        self.zPlane.plotItem.showGrid(True, True)
        self.plot_unit_circle()

        self.zeros = np.array([0 + 1j], dtype=complex)
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

    def calculate_and_plot_magnitude(self):
        self.points_on_the_circle = self.calculate_points_on_circle()
        mag = 20 * np.log10(self.get_the_mag().flatten())

        self.magPlot.plotItem.showGrid(True, True)
        self.magPlot.clear()
        self.magPlot.plot(mag)

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

    def get_the_mag(self):
        distance_of_zeros, distance_of_poles = 1, 1
        if self.zeros.size > 0:
            distance_of_zeros = np.abs(self.zeros - self.points_on_the_circle)
        if self.poles.size > 0:
            distance_of_poles = np.abs(self.poles - self.points_on_the_circle)

        return (distance_of_zeros / distance_of_poles)


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
