from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QDoubleValidator, QFont
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication

class SideMenu(QtWidgets.QWidget):
    zoomed_in = pyqtSignal(bool)
    zoomed_out = pyqtSignal(bool)
    rotated_right = pyqtSignal(bool)
    rotated_left = pyqtSignal(bool)

    up = pyqtSignal(bool)
    down = pyqtSignal(bool)
    left = pyqtSignal(bool)
    right = pyqtSignal(bool)

    add = pyqtSignal(bool)
    edit = pyqtSignal(bool)
    remove = pyqtSignal(bool)
    transform = pyqtSignal(bool)

    def __init__(self, max_width):
        QtWidgets.QWidget.__init__(self)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.title = QtWidgets.QLabel('Menu de funções')
        self.list = QtWidgets.QListWidget()
        text_size = 14
        self.add_btn = self.set_button('Add', lambda e: self.add.emit(True), text_size)
        self.edit_btn = self.set_button('Edit', lambda e: self.edit.emit(True), text_size)
        self.remove_btn = self.set_button('Remove', lambda e: self.remove.emit(True), text_size)
        self.transform_btn = self.set_button('Transform', lambda e: self.transform.emit(True), text_size)
        self.step = QLineEdit()
        self.step.setPlaceholderText("Navigation Steps");
        self.step.setValidator(QDoubleValidator());

        self.steps_label = QtWidgets.QLabel('Step: ')

        button_size = 20
        self.zoom_in_label = self.set_button("&#128269;+", lambda e: self.zoomed_in.emit(True), button_size)
        self.zoom_out_label = self.set_button("&#128269;-", lambda e: self.zoomed_out.emit(True), button_size)
        self.rotate_left_label = self.set_button("&#8630;", lambda e: self.rotated_left.emit(True), button_size)
        self.rotate_right_label = self.set_button("&#8631;", lambda e: self.rotated_right.emit(True), button_size)

        self.left_btn = self.set_button("&#8678;", lambda e: self.left.emit(True), button_size)
        self.right_btn = self.set_button("&#8680;", lambda e: self.right.emit(True), button_size)
        self.up_btn = self.set_button("&#8679;", lambda e: self.up.emit(True), button_size)
        self.down_btn = self.set_button("&#8681;", lambda e: self.down.emit(True), button_size)


        self.x_axis_label = QtWidgets.QLabel('X:')
        self.x_axis_check = QtWidgets.QRadioButton()
        self.y_axis_label = QtWidgets.QLabel('Y:')
        self.y_axis_check = QtWidgets.QRadioButton()
        self.z_axis_label = QtWidgets.QLabel('Z:')
        self.z_axis_check = QtWidgets.QRadioButton()
        self.z_axis_check.setChecked(True)



        self.navigation_layout = QtWidgets.QGridLayout()
        self.edit_layout = QtWidgets.QGridLayout()


        self.layout.addWidget(self.title)
        self.layout.addWidget(self.list)
        self.layout.addLayout(self.edit_layout)
        self.layout.addLayout(self.navigation_layout)

        self.edit_layout.addWidget(self.add_btn, 0,0)
        self.edit_layout.addWidget(self.remove_btn, 0,1)
        self.edit_layout.addWidget(self.edit_btn, 1,0, 1, 2)
        self.edit_layout.addWidget(self.transform_btn, 2,0, 1,2)

        self.navigation_layout.addWidget(self.steps_label, 0,0,1,2)
        self.navigation_layout.addWidget(self.step, 0,2,1,4)
        self.navigation_layout.addWidget(self.rotate_left_label, 1,0,1,2)
        self.navigation_layout.addWidget(self.up_btn, 1,2,1,2)
        self.navigation_layout.addWidget(self.rotate_right_label, 1,4,1,2)
        self.navigation_layout.addWidget(self.left_btn, 2,0,1,2)
        self.navigation_layout.addWidget(self.right_btn,2,4,1,2)
        self.navigation_layout.addWidget(self.down_btn, 3,2,1,2)
        self.navigation_layout.addWidget(self.zoom_in_label, 3,0,1,2)
        self.navigation_layout.addWidget(self.zoom_out_label, 3,4,1,2)
        
        self.navigation_layout.addWidget(self.x_axis_label, 4,0)
        self.navigation_layout.addWidget(self.x_axis_check, 4,1)
        self.navigation_layout.addWidget(self.y_axis_label, 4,2)
        self.navigation_layout.addWidget(self.y_axis_check, 4,3)
        self.navigation_layout.addWidget(self.z_axis_label, 4,4)
        self.navigation_layout.addWidget(self.z_axis_check, 4,5)

        self.setMaximumWidth(max_width)


    def make_list(self,obj_list):
        self.list.clear()
        self.list.addItems(obj_list)


    def set_button(self, html, onclick, size):
        label = QtWidgets.QLabel("<span>"+html+"</span>")
        label.mousePressEvent = onclick
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet(
            "QLabel"
            "{"
            " border-style: outset;"
            " border-width:2px;"
            " border-radius:5px;"
            " font: bold "+str(size)+"px;"
            " border-color: #8F8F8F;"
            "}"
            "QLabel::hover {border-color:#AFAFAF;}")
        label.enterEvent = pointerCursor
        label.leaveEvent = restoreCursor

        return label

def pointerCursor(e):
    QApplication.setOverrideCursor(Qt.PointingHandCursor)

def restoreCursor(e):
    QApplication.restoreOverrideCursor()