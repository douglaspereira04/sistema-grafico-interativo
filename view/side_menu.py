from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QDoubleValidator, QFont
from PyQt5.QtCore import Qt

class SideMenu(QtWidgets.QWidget):
    def __init__(self, max_width):
        QtWidgets.QWidget.__init__(self)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.title = QtWidgets.QLabel('Menu de funções')
        self.list = QtWidgets.QListWidget()
        self.add_btn = QtWidgets.QPushButton('Add')
        self.edit_btn = QtWidgets.QPushButton('Edit')
        self.remove_btn = QtWidgets.QPushButton('Del')
        self.transform_btn = QtWidgets.QPushButton('Transform')
        self.step = QLineEdit()
        self.step.setPlaceholderText("Navigation Steps");
        self.step.setValidator(QDoubleValidator());

        self.steps_label = QtWidgets.QLabel('Step: ')
        self.zoom_label = QtWidgets.QLabel('Zoom: ')

        self.left_btn = QtWidgets.QPushButton('<')
        self.right_btn = QtWidgets.QPushButton('>')
        self.up_btn = QtWidgets.QPushButton('^')
        self.down_btn = QtWidgets.QPushButton('v')
        self.forward_btn = QtWidgets.QPushButton('F')
        self.backward_btn = QtWidgets.QPushButton('B')
        self.zin_btn = QtWidgets.QPushButton('+')
        self.zout_btn = QtWidgets.QPushButton('-')
        self.x_axis_label = QtWidgets.QLabel('X:')
        self.x_axis_check = QtWidgets.QCheckBox()
        self.y_axis_label = QtWidgets.QLabel('Y:')
        self.y_axis_check = QtWidgets.QCheckBox()
        self.z_axis_label = QtWidgets.QLabel('Z:')
        self.z_axis_check = QtWidgets.QCheckBox()
        self.rotation_button = QtWidgets.QPushButton('Rotate')
        self.rotation_slider = QtWidgets.QSlider(Qt.Horizontal)



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
        self.navigation_layout.addWidget(self.up_btn, 1,2,1,2)
        self.navigation_layout.addWidget(self.left_btn, 2,0,1,2)
        self.navigation_layout.addWidget(self.right_btn,2,4,1,2)
        self.navigation_layout.addWidget(self.down_btn, 3,2,1,2)
        self.navigation_layout.addWidget(self.forward_btn, 1,4,1,2)
        self.navigation_layout.addWidget(self.backward_btn, 3,4,1,2)
        self.navigation_layout.addWidget(self.zoom_label, 5,0, 1,2)
        self.navigation_layout.addWidget(self.zin_btn, 5,2,1,2)
        self.navigation_layout.addWidget(self.zout_btn, 5,4,1,2)
        self.navigation_layout.addWidget(self.x_axis_label, 6,0)
        self.navigation_layout.addWidget(self.x_axis_check, 6,1)
        self.navigation_layout.addWidget(self.y_axis_label, 6,2)
        self.navigation_layout.addWidget(self.y_axis_check, 6,3)
        self.navigation_layout.addWidget(self.z_axis_label, 6,4)
        self.navigation_layout.addWidget(self.z_axis_check, 6,5)
        self.navigation_layout.addWidget(self.rotation_button, 7,0, 1,3)
        self.navigation_layout.addWidget(self.rotation_slider, 7,3,1,3)

        self.setMaximumWidth(max_width)


    def make_list(self,obj_list):
        self.list.clear()
        self.list.addItems(obj_list)