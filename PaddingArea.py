import sys
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QElapsedTimer


class PaddingArea(QWidget):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.elapsed_timer = QElapsedTimer()
        self.first_time_enter = True
        self.pause_time = 0
        self.initUI()

    def initUI(self):
        # Start capturing mouse movement
        self.setMouseTracking(True)

    def enterEvent(self, event):
        if self.first_time_enter and self.mainWindow.input_mode == "custom":
            self.first_time_enter = False
            self.elapsed_timer.start()

    def leaveEvent(self, event):
        # Stop collecting data when leaving the widget
        if not self.first_time_enter and self.mainWindow.input_mode == "custom":
            self.pause_time = self.elapsed_timer.elapsed()

    def mouseMoveEvent(self, event):
        # Capture mouse movement and update data while inside the widget
        if not self.first_time_enter and self.mainWindow.input_mode == "custom":
            y = event.y()
            # Get the current elapsed time in milliseconds
            current_elapsed_time = self.elapsed_timer.elapsed()
            # Calculate the adjusted elapsed time by subtracting the pause time
            elapsed_time_ms = current_elapsed_time - self.pause_time
            # Append the elapsed time in milliseconds to the time list
            self.mainWindow.signal.time.append(elapsed_time_ms)
            self.mainWindow.signal.data.append(y)
            self.mainWindow.plot_input_and_output_signal()
