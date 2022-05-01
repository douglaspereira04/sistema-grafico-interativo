from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QIntValidator

class SideMenu(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.title = QtWidgets.QLabel('Menu de funções')
        self.list = QtWidgets.QListWidget()
        self.add_btn = QtWidgets.QPushButton('Add')
        self.step = QLineEdit()
        self.step.setPlaceholderText("Navigation Steps");
        self.step.setValidator(QIntValidator());

        self.steps_label = QtWidgets.QLabel('Steps')
        self.zoom_label = QtWidgets.QLabel('Zoom')

        self.left_btn = QtWidgets.QPushButton('<')
        self.right_btn = QtWidgets.QPushButton('>')
        self.up_btn = QtWidgets.QPushButton('^')
        self.down_btn = QtWidgets.QPushButton('v')
        self.zin_btn = QtWidgets.QPushButton('+')
        self.zout_btn = QtWidgets.QPushButton('-')

        self.navigation_layout = QtWidgets.QGridLayout()


        self.layout.addWidget(self.title)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.add_btn)
        self.layout.addLayout(self.navigation_layout)

        self.navigation_layout.addWidget(self.steps_label, 0,0)
        self.navigation_layout.addWidget(self.step, 0,1,1,2)
        self.navigation_layout.addWidget(self.up_btn, 1,1)
        self.navigation_layout.addWidget(self.left_btn, 2,0)
        self.navigation_layout.addWidget(self.right_btn,2,2)
        self.navigation_layout.addWidget(self.down_btn, 3,1)
        self.navigation_layout.addWidget(self.zoom_label, 4,0)
        self.navigation_layout.addWidget(self.zin_btn, 4,1)
        self.navigation_layout.addWidget(self.zout_btn, 4,2)

        self.setMaximumWidth(150)


    def make_list(self,obj_list):
        self.list.clear()
        self.list.addItems(obj_list)
