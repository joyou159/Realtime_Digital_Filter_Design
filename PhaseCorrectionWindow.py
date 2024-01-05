from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFileDialog, QMessageBox, QColorDialog, QListWidgetItem, QPushButton
from PyQt6.QtGui import QIcon
import numpy as np


class PhaseCorrectionWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(PhaseCorrectionWindow, self).__init__(parent)
        uic.loadUi('phaseCorrection.ui', self)
        self.setWindowTitle("Phase Correction")
        self.destroyed.connect(self.on_window_closed)
        self.add.clicked.connect(self.add_filter)
        self.mainWindow = self.parent()
        # Plot the phase response
        self.allPassPhase.plotItem.showGrid(True, True)

        self.allPassPhase.setLabel('left', 'Phase (radians)')
        self.allPassPhase.setLabel('bottom', 'Frequency (Hz)')
        # Plot the phase response
        self.originalPhase.plotItem.showGrid(True, True)

        self.originalPhase.setLabel('left', 'Phase (radians)')
        self.originalPhase.setLabel('bottom', 'Frequency (Hz)')

    def on_window_closed(self):
        self.close()

    def add_filter(self):
        text = self.lineEdit.text()

        custom_widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(text)
        label.setStyleSheet("color:white")

        icon_button = QPushButton()
        # Set the path to your icon file
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
        icon_button.setStyleSheet("background-color:transparent")
        icon_button.clicked.connect(
            lambda: self.delete_from_filters(custom_widget))

        layout.addWidget(icon_button)
        layout.addWidget(label)
        custom_widget.setLayout(layout)

        # Create a QListWidgetItem and set the custom widget as the display widget
        item = QListWidgetItem()
        item.setSizeHint(custom_widget.sizeHint())
        self.filtersList.addItem(item)
        self.filtersList.setItemWidget(item, custom_widget)

        new_filter = complex(text)
        self.mainWindow.phase_correction_filters.append(new_filter)

        self.mainWindow.zeros_all_pass = np.append(
            self.mainWindow.zeros, 1 / new_filter.conjugate())
        self.mainWindow.poles_all_pass = np.append(
            self.mainWindow.poles, new_filter)

        self.lineEdit.clear()
        self.plot_graphs()

    def delete_from_filters(self, custom_widget):
        # Find the corresponding item in the QListWidget
        item = self.filtersList.itemAt(custom_widget.pos())
        if item is not None:
            row = self.filtersList.row(item)
            self.filtersList.takeItem(row)

            if 0 <= row < len(self.mainWindow.phase_correction_filters):
                removed_filter = self.mainWindow.phase_correction_filters.pop(
                    row)
                self.mainWindow.zeros_all_pass = [
                    z for z in self.mainWindow.zeros if z != 1 / removed_filter.conjugate()]
                self.mainWindow.poles_all_pass = [
                    p for p in self.mainWindow.poles if p != removed_filter]

        self.plot_graphs()

    def plot_graphs(self):
        w, _, phase_original = self.mainWindow.get_the_mag_and_phase(
            self.mainWindow.zeros, self.mainWindow.poles)
        w1, _, phase_all_pass = self.mainWindow.get_the_mag_and_phase(
            np.concatenate((self.mainWindow.zeros, self.mainWindow.zeros_all_pass),
                           axis=0), np.concatenate((self.mainWindow.poles, self.mainWindow.poles_all_pass), axis=0))

        self.allPassPhase.clear()
        self.allPassPhase.plot(w, phase_original)

        self.originalPhase.clear()
        self.originalPhase.plot(w1, phase_all_pass)
