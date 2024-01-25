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
            
            self.numerator, self.denominator = zpk2tf(
                self.mainWindow.zeros, self.mainWindow.poles, 1)

            # Get the order of the numerator and denominator
            self.order = (len(self.numerator) - 1) + (len(self.denominator) - 1)
            
            if len(self.mainWindow.signal.data)< self.order:
                self.mainWindow.signal.data = [0.21] * abs(len(self.mainWindow.signal.data) - self.order)
        

    def mouseMoveEvent(self, event):
        if not self.first_time_enter and self.mainWindow.input_mode == "custom":
            y = event.y()
            self.mainWindow.signal.data.append(y)
            self.plot()


    def plot(self):
        if self.mainWindow.signal.data:
            # print(self.mainWindow.signal.data)
            print(self.order)
            input_data = self.mainWindow.signal.data[-1 * self.order :]
            print(input_data)
            output_points_after_filter = np.real(
                lfilter(self.numerator, self.denominator, input_data))
            
            self.mainWindow.signal.output_signal_after_filter.append(
                output_points_after_filter[-1])
            
            print(self.mainWindow.signal.output_signal_after_filter)

            # Plot updated output signal
            self.mainWindow.outputSignal.plot(
                self.mainWindow.signal.output_signal_after_filter, pen='r')

            self.mainWindow.inputSignal.plot(
                self.mainWindow.signal.data, pen='b')
