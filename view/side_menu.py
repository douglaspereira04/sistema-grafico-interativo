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
        self.list.setMaximumWidth(100)
        self.list.setMaximumHeight(100)
        self.add_btn = QtWidgets.QPushButton('Add')
        self.factor = QLineEdit()
        self.factor.setPlaceholderText("Navigation multiplier");
        self.factor.setValidator(QIntValidator());
        self.left_btn = QtWidgets.QPushButton('Left')
        self.right_btn = QtWidgets.QPushButton('Right')
        self.up_btn = QtWidgets.QPushButton('Up')
        self.down_btn = QtWidgets.QPushButton('Down')
        self.zin_btn = QtWidgets.QPushButton('Zoom In')
        self.zout_btn = QtWidgets.QPushButton('Zoom Out')
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.add_btn)
        self.layout.addWidget(self.factor)
        self.layout.addWidget(self.left_btn)
        self.layout.addWidget(self.right_btn)
        self.layout.addWidget(self.up_btn)
        self.layout.addWidget(self.down_btn)
        self.layout.addWidget(self.zin_btn)
        self.layout.addWidget(self.zout_btn)


    def make_list(self,obj_list):
        self.list.clear()
        self.list.addItems(obj_list)
