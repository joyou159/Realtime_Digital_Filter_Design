import numpy as np
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QColor
from functools import partial
import pyqtgraph as pg


class UnitCircle:
    def __init__(self, main_window):
        # Create lists to store poles and zeros
        self.main_window = main_window
        self.poles = []
        self.zeros = []
        self.zPlane = self.main_window.zPlane
        self.zPlane.setLimits(xMin=-1.1, xMax=1.1, yMin=-1.1, yMax=1.1)
        self.zeros_button = self.main_window.zeros
        self.poles_button = self.main_window.poles
        self.zeros_button_pressed = False
        self.poles_button_pressed = False
        self.clicked_point = None  # for removing
        self.dragged_point = None
        self.drag_start_pos = None
        self.change_color()

        self.zeros_button.clicked.connect(self.handle_mode_of_insertion)
        self.poles_button.clicked.connect(self.handle_mode_of_insertion)

        # Set up the unit circle
        x, y = self.calculate_circle_points()
        self.update_plot(x, y)

        # Define symbol styles for poles and zeros
        self.pole_symbol = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255), symbol="x")
        self.zero_symbol = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255), symbol="o")

        # Add symbols to the plot item
        self.zPlane.addItem(self.pole_symbol)
        self.zPlane.addItem(self.zero_symbol)

        self.pole_symbol.setData(pos=self.poles)
        self.zero_symbol.setData(pos=self.zeros)

        # Connect sigClicked signal to the handler function
        self.pole_symbol.sigClicked.connect(
            lambda _, points: self.poleClicked(points))
        self.zero_symbol.sigClicked.connect(
            lambda _, points: self.zeroClicked(points))

        # Connect contextMenuEvent to the handler function
        self.zPlane.scene().sigMouseClicked.connect(self.mouseClickEvent)
        self.zPlane.scene().sigMouseClicked.connect(self.contextMenuEvent)

    def calculate_circle_points(self, num_points=100):
        # Calculate points on the unit circle
        theta = 2 * np.pi * np.linspace(0, 1, num_points)
        x = np.cos(theta)
        y = np.sin(theta)
        return x, y

    def handle_mode_of_insertion(self):
        source = self.main_window.sender()
        print("came here")

        if source is self.zeros_button and not self.zeros_button_pressed:
            self.zeros_button_pressed = True
            self.poles_button_pressed = False
            self.change_color()
        elif source is self.poles_button and not self.poles_button_pressed:
            self.poles_button_pressed = True
            self.zeros_button_pressed = False
            self.change_color()

    def change_color(self):
        # Set the color of the zeros_button
        zeros_color = QColor(
            0, 0, 255) if self.zeros_button_pressed else QColor(255, 0, 0)
        self.zeros_button.setStyleSheet(
            f'background-color: {zeros_color.name()};')

        # Set the color of the poles_button
        poles_color = QColor(
            0, 0, 255) if self.poles_button_pressed else QColor(255, 0, 0)
        self.poles_button.setStyleSheet(
            f'background-color: {poles_color.name()};')

    def poleClicked(self, points):
        # Handle pole click event
        pos = points[0].pos()
        self.add_pole(pos)

    def zeroClicked(self, points):
        # Handle zero click event
        pos = points[0].pos()
        self.add_zero(pos)

    def update_plot(self, x, y):
        # Clear existing data and add new data
        self.zPlane.clear()
        self.zPlane.plot(x, y)

    def add_pole(self, pos):
        # Add a pole to the unit circle
        self.poles.append(pos)
        self.pole_symbol.setData(pos=self.poles)

    def add_zero(self, pos):
        # Add a zero to the unit circle
        self.zeros.append(pos)
        self.zero_symbol.setData(pos=self.zeros)

    def remove_point(self, item, pos):
        # Remove a pole or zero
        if item == 'pole':
            self.poles.remove(pos)
            self.pole_symbol.setData(pos=self.poles)
        elif item == 'zero':
            self.zeros.remove(pos)
            self.zero_symbol.setData(pos=self.zeros)

    def mouseClickEvent(self, event):
        if self.poles_button_pressed or self.zeros_button_pressed:
            # Handle mouse clicks to add or remove poles/zeros
            pos = self.zPlane.plotItem.vb.mapSceneToView(event.scenePos())
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                if self.poles_button_pressed:
                    self.add_pole(pos)
                elif self.zeros_button_pressed:
                    self.add_zero(pos)
            elif event.button() == QtCore.Qt.MouseButton.RightButton:
                # Store the clicked point for the context menu
                self.clicked_point = pos

    def contextMenuEvent(self, event):
        # Handle right-click context menu to remove poles/zeros
        if self.clicked_point is not None:
            print("came here")
            menu = QtWidgets.QMenu()
            threshold = 0.1  # Increase the distance threshold if needed
            clicked_point = self.clicked_point  # Store the clicked point

            # Check if the clicked point is close to any poles
            for pole_pos in self.poles:
                if (pole_pos - clicked_point).manhattanLength() < threshold:
                    print("pole")
                    action = menu.addAction('Remove Pole')
                    action.triggered.connect(
                        partial(self.remove_point, 'pole', pole_pos))

            # Check if the clicked point is close to any zeros
            for zero_pos in self.zeros:
                if (zero_pos - clicked_point).manhattanLength() < threshold:
                    print("zero")
                    action = menu.addAction('Remove Zero')
                    action.triggered.connect(
                        partial(self.remove_point, 'zero', zero_pos))

            global_pos = self.zPlane.mapToGlobal(
                self.zPlane.mapFromScene(event.scenePos()))
            action = menu.exec(global_pos)

            if action:
                # If an action was triggered, reset clicked point
                self.clicked_point = None
