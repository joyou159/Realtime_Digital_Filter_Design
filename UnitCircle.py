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

        self.zPlane = self.main_window.zPlane
        self.zPlane.setLimits(xMin=-1.1, xMax=1.1, yMin=-1.1, yMax=1.1)
        self.zeros_button = self.main_window.zeros
        self.poles_button = self.main_window.poles
        self.zeros_button_pressed = True
        self.poles_button_pressed = False
        self.clicked_point = None  # for removing
        self.dragged_point = None
        self.drag_start_pos = None
        self.clear_mode = self.main_window.Clear_selection.currentText()
        self.change_color()

        self.zeros_button.clicked.connect(self.handle_mode_of_insertion)
        self.poles_button.clicked.connect(self.handle_mode_of_insertion)
        self.main_window.Clear_selection.currentIndexChanged.connect(
            self.handle_clearing_mode)
        self.main_window.clear_button.clicked.connect(self.clear)

        # Set up the unit circle
        self.x, self.y = self.calculate_circle_points()
        self.update_plot(self.x, self.y)

        self.pole_symbol = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255), symbol="x")
        self.zero_symbol = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255), symbol="o")
        self.zPlane.addItem(self.pole_symbol)
        self.zPlane.addItem(self.zero_symbol)

        self.pole_symbol.setData(pos=self.Poles)
        self.zero_symbol.setData(pos=self.Zeros)

        self.pole_symbol.sigClicked.connect(
            lambda _, points: self.poleClicked(points))
        self.zero_symbol.sigClicked.connect(
            lambda _, points: self.zeroClicked(points))

        self.zPlane.scene().sigMouseClicked.connect(self.mouseClickEvent)
        self.zPlane.scene().sigMouseClicked.connect(self.contextMenuEvent)

    def clear(self):
        if self.clear_mode == "Zeros":
            self.Zeros = list()
        elif self.clear_mode == "Poles":
            self.Poles = list()
        else:
            self.Poles = list()
            self.Zeros = list()
        self.zero_symbol.setData(pos=self.Zeros)
        self.pole_symbol.setData(pos=self.Poles)

    def handle_clearing_mode(self):
        self.clear_mode = self.main_window.sender().currentText()

    def calculate_circle_points(self, num_points=100):
        theta = 2 * np.pi * np.linspace(0, 1, num_points)
        x = np.cos(theta)
        y = np.sin(theta)
        return x, y

    def handle_mode_of_insertion(self):
        source = self.main_window.sender()

        if source is self.zeros_button and not self.zeros_button_pressed:
            self.zeros_button_pressed = True
            self.poles_button_pressed = False
            self.change_color()
        elif source is self.poles_button and not self.poles_button_pressed:
            self.poles_button_pressed = True
            self.zeros_button_pressed = False
            self.change_color()

    def change_color(self):
        zeros_color = QColor(
            0, 0, 255) if self.zeros_button_pressed else QColor(255, 0, 0)
        self.zeros_button.setStyleSheet(
            f'background-color: {zeros_color.name()};')
        poles_color = QColor(
            0, 0, 255) if self.poles_button_pressed else QColor(255, 0, 0)
        self.poles_button.setStyleSheet(
            f'background-color: {poles_color.name()};')

    def poleClicked(self, points):
        pos = points[0].pos()
        self.add_pole(pos)

    def zeroClicked(self, points):
        pos = points[0].pos()
        self.add_zero(pos)

    def update_plot(self, x, y):
        self.zPlane.clear()
        self.zPlane.plot(x, y)
 
    def add_pole(self, pos):
        self.Poles.append(pos)
        self.pole_symbol.setData(pos=self.Poles)

    def add_zero(self, pos):
        self.Zeros.append(pos)
        self.zero_symbol.setData(pos=self.Zeros)

    def remove_point(self, item, pos):
        if item == 'pole':
            self.Poles.remove(pos)
            self.pole_symbol.setData(pos=self.Poles)
        elif item == 'zero':
            self.Zeros.remove(pos)
            self.zero_symbol.setData(pos=self.Zeros)

    def mouseClickEvent(self, event):
        # Handle mouse clicks to add or remove poles/zeros
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
                elif self.zeros_button_pressed:
                    if self.main_window.Conj_pair.isChecked():
                        self.add_zero(pos)
                        conjugate_pos = QPointF(pos.x(), -pos.y())
                        self.add_zero(conjugate_pos)
                    else:
                        self.add_zero(pos)
            elif event.button() == QtCore.Qt.MouseButton.RightButton:
                # Store the clicked point for the context menu
                self.clicked_point = pos

    def contextMenuEvent(self, event):
        # Handle right-click context menu to remove poles/zeros
        if self.clicked_point is not None:
            menu = QtWidgets.QMenu()
            threshold = 0.1  # Increase the distance threshold if needed
            clicked_point = self.clicked_point  # Store the clicked point

            # Check if the clicked point is close to any poles
            for pole_pos in self.Poles:
                if (pole_pos - clicked_point).manhattanLength() < threshold:
                    action = menu.addAction('Remove Pole')
                    action.triggered.connect(
                        partial(self.remove_point, 'pole', pole_pos))
                    self.zPlane.setMenuEnabled(False)

            # Check if the clicked point is close to any zeros
            for zero_pos in self.zeros:
                if (zero_pos - clicked_point).manhattanLength() < threshold:
                    action = menu.addAction('Remove Zero')
                    action.triggered.connect(
                        partial(self.remove_point, 'zero', zero_pos))
                    self.zPlane.setMenuEnabled(False)

            global_pos = self.zPlane.mapToGlobal(
                self.zPlane.mapFromScene(event.scenePos()))
            action = menu.exec(global_pos)

            if action:
                # If an action was triggered, reset clicked point
                self.clicked_point = None
                self.zPlane.setMenuEnabled(True)
