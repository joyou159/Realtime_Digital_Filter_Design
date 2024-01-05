import sys
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor


class PaddingArea(QWidget):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.timer = QTimer(self)
        self.first_time_enter = True
        self.elapsed_time = 0
        self.pause_time = 0
        self.initUI()

    def initUI(self):
        # Start capturing mouse movement
        self.setMouseTracking(True)

        # Connect the timeout signal of the QTimer to the update_data function
        self.timer.timeout.connect(self.update_data)
        self.timer.start(10)  # Set the timeout interval in milliseconds

    def enterEvent(self, event):
        if self.first_time_enter and self.mainWindow.input_mode == "custom":
            self.first_time_enter = False
            self.elapsed_time = 0  # Reset elapsed time
            self.timer.start()

    def leaveEvent(self, event):
        # Stop collecting data when leaving the widget
        if not self.first_time_enter and self.mainWindow.input_mode == "custom":
            self.timer.stop()
            self.pause_time = self.elapsed_time

    def update_data(self):
        # Capture mouse movement and update data periodically
        if not self.first_time_enter and self.mainWindow.input_mode == "custom":
            y = self.mapFromGlobal(QCursor.pos()).y()
            # Increment elapsed time with the timer interval
            self.elapsed_time += self.timer.interval()
            # Append the elapsed time in milliseconds to the time list
            self.mainWindow.signal.time.append(self.elapsed_time)
            self.mainWindow.signal.data.append(y)
            self.mainWindow.plot_input_and_output_signal()
