import numpy as np
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QPointF

from PyQt6.QtGui import QColor, QIcon
from functools import partial
import pyqtgraph as pg
import functools


class UnitCircle:
    def __init__(self, main_window):
        # Create lists to store poles and zeros
        self.main_window = main_window
        self.Poles = []
        self.Zeros = []
        self.zPlane = self.main_window.ui.zPlane
        self.zPlane.setXRange(-1.1, 1.1)
        self.zPlane.setYRange(-1.1, 1.1)
        self.zPlane.showGrid(x=True, y=True)
        self.zPlane.setBackground("transparent")
        self.zPlane.setMenuEnabled(False)
        self.zeros_button = self.main_window.ui.zerosButton
        self.poles_button = self.main_window.ui.polesButton
        self.zeros_button.setIcon(QIcon("Icons\circle.png"))
        self.poles_button.setIcon(QIcon("Icons\cross.png"))
        self.main_window.clear_button.setIcon(QIcon("Icons\clear.png"))
        self.zeros_button_pressed = True
        self.poles_button_pressed = False
        self.poles_conjugates = []
        self.zeros_conjugates = []
        self.conjugate_checked_for_dragging = False
        self.conjugate_of_drag = None

        self.clear_mode = self.main_window.ui.Clear_selection.currentText()
        # self.main_window.ui.Clear_selection.set()

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

    def update_z_plane_view(self):
        max_value = 1
        for item in self.Zeros + self.Poles:
            max_value = max(max_value, item.pos().x())
            max_value = max(max_value, item.pos().y())

        max_value += 0.2
        self.zPlane.setXRange(-max_value, max_value)
        self.zPlane.setYRange(-max_value, max_value)

    def add_pole(self, pos):
        curr_pole = self.draw_item(pos, "x", "r")
        self.Poles.append(curr_pole)

    def add_zero(self, pos):
        curr_zero = self.draw_item(pos, "o", "b")
        self.Zeros.append(curr_zero)

    def remove_item(self, pos, item):
        if item == 'pole':
            self.Poles.remove(pos)
            self.zPlane.removeItem(pos)
        elif item == 'zero':
            print(pos)
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
        item.sigPositionChanged.connect(
            lambda ev, item=item: self.update_positions(ev, item))
        item.mouseClickEvent = functools.partial(
            lambda ev, item=item: self.contextMenuEvent(ev, item))

        return item

    def change_color(self):
        # Update color for zeros_button
        zeros_color = QColor(
            64, 92, 245) if self.zeros_button_pressed else QColor(0, 0, 0)
        self.zeros_button.setStyleSheet(
            f'background-color: {zeros_color.name()}; border: 1px solid gray; padding: 6px;  border-radius: 6px;font-size: 14px;')

        # Update color for poles_button
        poles_color = QColor(
            64, 92, 245) if self.poles_button_pressed else QColor(0, 0, 0)
        self.poles_button.setStyleSheet(
            f'background-color: {poles_color.name()}; border: 1px solid gray; padding: 6px;  border-radius: 6px;font-size: 14px;')

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
                        self.poles_conjugates.append(
                            (self.Poles[-1], self.Poles[-2]))
                    else:
                        self.add_pole(pos)

                if self.zeros_button_pressed:
                    if self.main_window.Conj_pair.isChecked():
                        self.add_zero(pos)
                        conjugate_pos = QPointF(pos.x(), -pos.y())
                        self.add_zero(conjugate_pos)
                        self.zeros_conjugates.append(
                            (self.Zeros[-1], self.Zeros[-2]))
                    else:
                        self.add_zero(pos)

                self.main_window.update_zeros_poles()
                self.plotting()

    def update_positions(self, event, item):
        if self.main_window.Conj_pair.isChecked():
            self.conjugate_of_drag = self.get_conjugate(item)
            if self.conjugate_of_drag:
                self.conjugate_of_drag.setPos(item.pos().x(), - item.pos().y())
        self.main_window.update_zeros_poles()
        self.plotting()

    def get_conjugate(self, item):
        if item in self.Poles:
            for conjugates in self.poles_conjugates:
                if item in conjugates:
                    conjugate = conjugates[0] if conjugates[0] != item else conjugates[1]
                    return conjugate

        elif item in self.Zeros:
            for conjugates in self.zeros_conjugates:
                if item in conjugates:
                    conjugate = conjugates[0] if conjugates[0] != item else conjugates[1]
                    return conjugate

        return None

    def contextMenuEvent(self, event, curr_item):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            menu = QtWidgets.QMenu()

            for pole_pos in self.Poles:
                if pole_pos == curr_item:
                    action_1 = menu.addAction('Remove Pole')
                    action_2 = menu.addAction('Swap to Zero')
                    action_1.triggered.connect(
                        partial(self.remove_action, pole_pos, 'pole'))
                    action_2.triggered.connect(
                        partial(self.swap_action, pole_pos, 'pole'))

            for zero_pos in self.Zeros:
                if zero_pos == curr_item:
                    action_1 = menu.addAction('Remove Zero')
                    action_2 = menu.addAction('Swap to Pole')
                    action_1.triggered.connect(
                        partial(self.remove_action,  zero_pos, 'zero'))
                    action_2.triggered.connect(
                        partial(self.swap_action, zero_pos, 'zero'))

            global_pos = self.zPlane.mapToGlobal(
                self.zPlane.mapFromScene(event.scenePos()))
            action = menu.exec(global_pos)

            # If an action was triggered, reset clicked point
            if action:
                self.main_window.update_zeros_poles()
                self.plotting()

    def plotting(self):
        self.main_window.plot_magnitude_and_phase()
        self.main_window.outputSignal.clear()
        self.main_window.inputSignal.clear()
        if len(self.main_window.signal.data):
            self.main_window.plot_input_and_output_signal()

    def calculate_circle_points(self, num_points=300):
        theta = 2 * np.pi * np.linspace(0, 1, num_points)
        x = np.cos(theta)
        y = np.sin(theta)
        return x, y

    def update_plot(self, x, y):
        self.zPlane.clear()
        pen_color = QColor(255, 255, 255)
        line_width = 2
        self.zPlane.plot(x, y, pen=pg.mkPen(
            color=pen_color, width=line_width))
        vLine = pg.InfiniteLine(
            pos=0, angle=90, movable=False, pen=(255, 255, 255))
        hLine = pg.InfiniteLine(
            pos=0, angle=0, movable=False, pen=(255, 255, 255))
        self.zPlane.addItem(vLine)
        self.zPlane.addItem(hLine)

    def swap_action(self, item, identity):
        if self.main_window.Conj_pair.isChecked():
            conjugate_item = self.get_conjugate(item)
            self.swap_item_identity(item, identity)
            if conjugate_item:
                self.swap_item_identity(conjugate_item, identity)
                self.add_swapped_conjugates(identity)  # last 2
                self.handle_conjugates_lists(item, identity)
        else:
            self.swap_item_identity(item, identity)

    def add_swapped_conjugates(self, identity):
        if identity == "pole":
            self.zeros_conjugates.append((self.Zeros[-1], self.Zeros[-2]))
        else:
            self.poles_conjugates.append((self.Poles[-1], self.Poles[-2]))

    def remove_action(self, item, identity):
        if self.main_window.Conj_pair.isChecked():
            conjugate_item = self.get_conjugate(item)
            if conjugate_item:
                self.remove_item(conjugate_item, identity)
        self.remove_item(item, identity)

    def swap_item_identity(self, item, identity):
        if identity == "zero":
            self.remove_item(item, identity)
            self.add_pole(item.pos())
        else:
            self.remove_item(item, identity)
            self.add_zero(item.pos())

    def handle_conjugates_lists(self, item, identity):
        if identity == "pole":
            for conjugates in self.poles_conjugates:
                if item in conjugates:
                    self.poles_conjugates.remove(conjugates)
        else:
            for conjugates in self.zeros_conjugates:
                if item in conjugates:
                    self.zeros_conjugates.remove(conjugates)
