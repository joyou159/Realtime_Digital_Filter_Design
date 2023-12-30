from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QVBoxLayout,  QMessageBox,  QSlider, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6 import QtWidgets, uic
import numpy as np
import pandas as pd
import sys
import pyqtgraph as pg
import qdarkstyle
import os


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        """
        Initializes the MainWindow class.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        super(MainWindow, self).__init__(*args, **kwargs)

        # Initialize instance variables
        self.init_ui()

    def show_error_message(self, message):
        """
        Displays an error message to the user.

        Args:
            message (str): The error message to be displayed.

        Returns:
            None
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()

    def set_icon(self, widget_name, icon_path):
        """
        Set the icon for a widget.

        Args:
            widget_name (str): The name of the widget.
            icon_path (str): The path to the icon file.

        Returns:
            None
        """
        # Load an icon
        icon = QIcon(icon_path)
        # Set the icon for the button
        widget_name.setIcon(icon)

    def openNewWindow(self):

        # disable the interactivity in the main window
        self.setEnabled(False)
        self.new_window = QtWidgets.QMainWindow()

        uic.loadUi('phaseCorrection.ui', self.new_window)

        # Connect the close event to a custom function
        self.new_window.closeEvent = self.on_close_event
        self.new_window.setWindowTitle("Phase Correction")
        self.new_window.show()
        self.new_window.destroyed.connect(self.onNewWindowClosed)

    def on_close_event(self, event):
        self.setEnabled(True)

    def onNewWindowClosed(self):
        self.new_window.close()
        self.setEnabled(True)


####################################### Main Window ########################################


    def init_ui(self):
        """
        Initializes the user interface.
        """
        # Load the UI Page
        self.ui = uic.loadUi('Mainwindow.ui', self)
        self.setWindowTitle("Realtime Digital Filter Design")
        self.ui.correctPhase.clicked.connect(self.openNewWindow)


def main():
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
