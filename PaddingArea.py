import sys
from PyQt6.QtWidgets import QWidget
import numpy as np
import sys
from scipy.signal import freqz, zpk2tf, lfilter


class PaddingArea(QWidget):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.first_time_enter = True
        self.pause_time = 0
        self.initUI()

    def initUI(self):
        # Start capturing mouse movement
        self.setMouseTracking(True)

    def enterEvent(self, event):
        if self.first_time_enter and self.mainWindow.input_mode == "custom":
            self.mainWindow.idx = 0
            self.mainWindow.outputSignal.clear()
            self.mainWindow.inputSignal.clear()
            self.mainWindow.signal.data = []
            self.mainWindow.signal.output_signal_after_filter = []
            self.first_time_enter = False

    def mouseMoveEvent(self, event):
        if not self.first_time_enter and self.mainWindow.input_mode == "custom":
            y = event.y()
            self.mainWindow.signal.data.append(y)
            self.plot()

    def plot(self):
        numerator, denominator = zpk2tf(
            self.mainWindow.zeros, self.mainWindow.poles, 1)

        # Get the order of the numerator and denominator
        order = (len(numerator) - 1) + (len(denominator) - 1)

        self.mainWindow.signal.output_signal_after_filter = np.real(
            lfilter(numerator, denominator, self.mainWindow.signal.data))
        # Plot updated output signal
        self.mainWindow.outputSignal.plot(
            self.mainWindow.signal.output_signal_after_filter, pen='r')

        self.mainWindow.inputSignal.plot(
            self.mainWindow.signal.data, pen='b')
