import numpy as np
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QPointF

from PyQt6.QtGui import QColor
from functools import partial
import pyqtgraph as pg


class UnitCircle:
    def __init__(self, main_window):
        # Create lists to store poles and zeros
        self.main_window = main_window
        self.Poles = []
        self.Zeros = []
        self.zPlane = self.main_window.ui.zPlane
        self.zPlane.hideAxis('bottom')
        self.zPlane.hideAxis('left')
        self.zPlane.setLimits(xMin=-1.1, xMax=1.1, yMin=-1.1, yMax=1.1)
        self.zeros_button = self.main_window.ui.zerosButton
        self.poles_button = self.main_window.ui.polesButton
        self.zeros_button_pressed = True
        self.poles_button_pressed = False
        self.clear_mode = self.main_window.ui.Clear_selection.currentText()
        self.change_color()

        self.zeros_button.clicked.connect(self.handle_mode_of_insertion)
        self.poles_button.clicked.connect(self.handle_mode_of_insertion)
        self.main_window.Clear_selection.currentIndexChanged.connect(
            self.handle_clearing_mode)
        self.main_window.clear_button.clicked.connect(self.clear)

        # Set up the unit circle
        self.x, self.y = self.calculate_circle_points()
        self.update_plot(self.x, self.y)

        self.zPlane.scene().sigMouseClicked.connect(self.handleMouseClick)

    def add_pole(self, pos):
        curr_pole = self.draw_item(pos, "x", "r")
        self.Poles.append(curr_pole)

    def add_zero(self, pos):
        curr_zero = self.draw_item(pos, "o", "b")
        self.Zeros.append(curr_zero)

    def remove_point(self, item, pos):
        if item == 'pole':
            self.Poles.remove(pos)
            self.zPlane.removeItem(pos)
        elif item == 'zero':
            self.Zeros.remove(pos)
            self.zPlane.removeItem(pos)

    def draw_item(self, pos, symbol, color):
        item = pg.TargetItem(
            pos=pos,
            size=10,
            movable=True,
            symbol=symbol,
            pen=pg.mkPen(color),
        )
        self.zPlane.addItem(item)
        # Connect the sigPositionChanged signal to the update_positions function
        item.sigPositionChanged.connect(lambda: self.update_positions(item))
        item.getViewBox().mouseClickEvent = lambda ev: self.contextMenuEvent(ev, item)
        return item

    def change_color(self):
        if self.zeros_button_pressed:
            zeros_color = QColor(
                255, 0, 0)
        else:
            zeros_color = QColor()
        self.zeros_button.setStyleSheet(
            f'background-color: {zeros_color.name()};')

        if self.poles_button_pressed:
            poles_color = QColor(
                255, 0, 0)
        else:
            poles_color = QColor()
        self.poles_button.setStyleSheet(
            f'background-color: {poles_color.name()};')

    def handle_mode_of_insertion(self):
        source = self.main_window.ui.sender()
        if source is self.zeros_button:
            self.zeros_button_pressed = True
            self.poles_button_pressed = False
            self.change_color()
        elif source is self.poles_button:
            self.poles_button_pressed = True
            self.zeros_button_pressed = False
            self.change_color()

    def handle_clearing_mode(self):
        self.clear_mode = self.main_window.ui.sender().currentText()

    def clear(self):
        if self.clear_mode == "Zeros":
            self.clear_items(self.Zeros)
            self.Zeros = list()

        elif self.clear_mode == "Poles":
            self.clear_items(self.Poles)
            self.Poles = list()
        else:
            self.clear_items(self.Poles)
            self.clear_items(self.Zeros)
            self.Poles = list()
            self.Zeros = list()

        self.main_window.update_zeros_poles()
        self.plotting()

    def clear_items(self, list_of_items):
        for item in list_of_items:
            self.zPlane.removeItem(item)

    def handleMouseClick(self, event):
        if self.poles_button_pressed or self.zeros_button_pressed:
            pos = self.zPlane.plotItem.vb.mapSceneToView(event.scenePos())
            if event.button() == QtCore.Qt.MouseButton.LeftButton:

                if self.poles_button_pressed:
                    if self.main_window.Conj_pair.isChecked():
                        self.add_pole(pos)
                        conjugate_pos = QPointF(pos.x(), -pos.y())
                        self.add_pole(conjugate_pos)
                    else:
                        self.add_pole(pos)

                if self.zeros_button_pressed:
                    if self.main_window.Conj_pair.isChecked():
                        self.add_zero(pos)
                        conjugate_pos = QPointF(pos.x(), -pos.y())
                        self.add_zero(conjugate_pos)
                    else:
                        self.add_zero(pos)

                self.main_window.update_zeros_poles()
                self.plotting()

    def update_positions(self, item):
        self.main_window.update_zeros_poles()
        self.plotting()

    def contextMenuEvent(self, event, curr_item):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            menu = QtWidgets.QMenu()
            print(type(curr_item))

            for pole_pos in self.Poles:
                if pole_pos == curr_item:
                    action = menu.addAction('Remove Pole')
                    action.triggered.connect(
                        partial(self.remove_point, 'pole', pole_pos))
                    self.zPlane.setMenuEnabled(False)

            for zero_pos in self.Zeros:
                if zero_pos == curr_item:
                    action = menu.addAction('Remove Zero')
                    action.triggered.connect(
                        partial(self.remove_point, 'zero', zero_pos))
                    self.zPlane.setMenuEnabled(False)

            global_pos = self.zPlane.mapToGlobal(
                self.zPlane.mapFromScene(event.scenePos()))
            action = menu.exec(global_pos)

            if action:
                # If an action was triggered, reset clicked point
                self.zPlane.setMenuEnabled(True)
                self.main_window.update_zeros_poles()
                self.plotting()

    def plotting(self):
        self.main_window.plot_magnitude_and_phase()
        self.main_window.outputSignal.clear()
        self.main_window.inputSignal.clear()
        if len(self.main_window.signal.data):
            self.main_window.plot_input_and_output_signal()

    def calculate_circle_points(self, num_points=100):
        theta = 2 * np.pi * np.linspace(0, 1, num_points)
        x = np.cos(theta)
        y = np.sin(theta)
        return x, y

    def update_plot(self, x, y):
        self.zPlane.clear()
        self.zPlane.plot(x, y)
        vLine = pg.InfiniteLine(
            pos=0, angle=90, movable=False, pen=(255, 255, 255))
        hLine = pg.InfiniteLine(
            pos=0, angle=0, movable=False, pen=(255, 255, 255))
        self.zPlane.addItem(vLine)
        self.zPlane.addItem(hLine)
