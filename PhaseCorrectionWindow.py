from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFileDialog, QMessageBox, QColorDialog, QListWidgetItem, QPushButton, QCheckBox
from PyQt6.QtGui import QIcon
import numpy as np
from PyQt6.QtCore import Qt, QElapsedTimer


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

        self.allPassPhase.setLabel('left', 'Phase (radian)')
        self.allPassPhase.setLabel('bottom', 'W (radian/sample)')
        # Plot the phase response
        self.originalPhase.plotItem.showGrid(True, True)

        self.originalPhase.setLabel('left', 'Phase (radian)')
        self.originalPhase.setLabel('bottom', 'W (radian/sample)')

        self.fill_filters_list()

        if self.mainWindow.poles_all_pass.size:
            self.plot_graphs()

        print("Poles All Pass:")

        for pole in self.mainWindow.poles_all_pass:
            print(pole)

        print("Zeros All Pass:")
        for zero in self.mainWindow.zeros_all_pass:
            print(zero)

        print("all Phase Correction Filters:")
        for phase_filter in self.mainWindow.all_phase_correction_filters:
            print(phase_filter)

        print("checked Phase Correction Filters:")
        for phase_filter in self.mainWindow.checked_phase_correction_filters:
            print(phase_filter)

    def on_window_closed(self):
        self.close()

    def add_filter(self):
        text = self.lineEdit.text()

        custom_widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(text)
        label.setStyleSheet("color:white")

        icon_button = QPushButton()
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
        icon_button.setStyleSheet("background-color:transparent")
        icon_button.clicked.connect(
            lambda: self.delete_from_filters(custom_widget))

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(
            lambda: self.handle_checkbox_change(complex(text), custom_widget)
        )

        layout.addWidget(icon_button)
        layout.addWidget(label)
        layout.addWidget(checkbox)
        custom_widget.setLayout(layout)

        item = QListWidgetItem()
        item.setSizeHint(custom_widget.sizeHint())
        self.filtersList.addItem(item)
        self.filtersList.setItemWidget(item, custom_widget)

        new_filter = complex(text)
        self.mainWindow.all_phase_correction_filters.append(new_filter)

        self.lineEdit.clear()

    def handle_checkbox_change(self, value, custom_widget):
        if self.sender().isChecked():
            new_filter = complex(value)
            self.mainWindow.checked_phase_correction_filters.append(new_filter)
            # Assuming self.mainWindow.zeros_all_pass and self.mainWindow.poles_all_pass are initially 1-dimensional arrays or empty
            if not self.mainWindow.zeros_all_pass.size:
                self.mainWindow.zeros_all_pass = np.array(
                    [1 / new_filter.conjugate()])
            else:
                self.mainWindow.zeros_all_pass = np.concatenate(
                    (self.mainWindow.zeros_all_pass, np.array([1 / new_filter.conjugate()])))

            if not self.mainWindow.poles_all_pass.size:
                self.mainWindow.poles_all_pass = np.array([new_filter])
            else:
                self.mainWindow.poles_all_pass = np.concatenate(
                    (self.mainWindow.poles_all_pass, np.array([new_filter])))

        else:
            removed_filter = complex(value)

            # Convert the lists to NumPy arrays
            self.mainWindow.checked_phase_correction_filters = [
                p for p in self.mainWindow.checked_phase_correction_filters if str(p) != str(removed_filter)]
            self.mainWindow.zeros_all_pass = np.array(
                [z for z in self.mainWindow.zeros_all_pass if str(z) != str(1 / removed_filter.conjugate())])
            self.mainWindow.poles_all_pass = np.array(
                [p for p in self.mainWindow.poles_all_pass if str(p) != str(removed_filter)])

        self.plot_graphs()

    def delete_from_filters(self, custom_widget):
        # Find the corresponding item in the QListWidget
        item = self.filtersList.itemAt(custom_widget.pos())
        if item is not None:
            row = self.filtersList.row(item)
            self.filtersList.takeItem(row)

            if 0 <= row < len(self.mainWindow.all_phase_correction_filters):
                removed_filter = complex(self.mainWindow.all_phase_correction_filters.pop(
                    row))

                # Convert the lists to NumPy arrays
                self.mainWindow.checked_phase_correction_filters = [
                    p for p in self.mainWindow.checked_phase_correction_filters if str(p) != str(removed_filter)]
                self.mainWindow.zeros_all_pass = np.array(
                    [z for z in self.mainWindow.zeros_all_pass if str(z) != str(1 / removed_filter.conjugate())])
                self.mainWindow.poles_all_pass = np.array(
                    [p for p in self.mainWindow.poles_all_pass if str(p) != str(removed_filter)])

            self.plot_graphs()

    def plot_graphs(self):
        w, _, phase_original = self.mainWindow.get_the_mag_and_phase(
            self.mainWindow.zeros, self.mainWindow.poles)
        w1, _, phase_all_pass = self.mainWindow.get_the_mag_and_phase(
            np.concatenate((self.mainWindow.zeros, self.mainWindow.zeros_all_pass),
                           axis=0), np.concatenate((self.mainWindow.poles, self.mainWindow.poles_all_pass), axis=0))

        self.allPassPhase.clear()
        self.allPassPhase.plot(w, phase_all_pass)

        self.originalPhase.clear()
        self.originalPhase.plot(w1, phase_original)

    def fill_filters_list(self):
        # Clear the existing items in the filtersList
        self.filtersList.clear()

        # Iterate over the poles and add items to the filtersList
        for phase_correction_filter in self.mainWindow.all_phase_correction_filters:
            self.add_filter_from_pole(phase_correction_filter)

        self.plot_graphs()

    def add_filter_from_pole(self, pole):
        custom_widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(str(pole))
        label.setStyleSheet("color:white")

        icon_button = QPushButton()
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
        icon_button.setStyleSheet("background-color:transparent")
        icon_button.clicked.connect(
            lambda: self.delete_from_filters(custom_widget))

        checkbox = QCheckBox()
        if pole in self.mainWindow.checked_phase_correction_filters:
            checkbox.setCheckState(Qt.CheckState.Checked)
        checkbox.stateChanged.connect(
            lambda: self.handle_checkbox_change(pole, custom_widget)
        )

        layout.addWidget(icon_button)
        layout.addWidget(label)
        layout.addWidget(checkbox)
        custom_widget.setLayout(layout)

        item = QListWidgetItem()
        item.setSizeHint(custom_widget.sizeHint())
        self.filtersList.addItem(item)
        self.filtersList.setItemWidget(item, custom_widget)
