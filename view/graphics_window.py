from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPlainTextEdit
from view.canvas import Canvas
from view.side_menu import SideMenu

class GraphicsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        ## Generate the structure parts of the MainWindow
        self.central_widget = QtWidgets.QWidget()  # A QWidget to work as Central Widget
        self.right_widget = QtWidgets.QWidget()  # A QWidget to work as Central Widget
        self.layout1 = QtWidgets.QVBoxLayout()  # Vertical Layout
        self.layout2 = QtWidgets.QHBoxLayout()  # Horizontal Layout
        self.layout3 = QtWidgets.QVBoxLayout()  # Vorizontal Layout
        self.canvas = Canvas(300,300)
        self.log = QPlainTextEdit(self)
        self.log.setReadOnly(True)

        self.side_menu = SideMenu()
        # self.exitBtn = QtWidgets.QPushButton('Exit')
        ## Build the structure
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout1)
        self.layout1.addLayout(self.layout2)
        self.layout2.addWidget(self.side_menu)
        self.layout2.addLayout(self.layout3)
        self.layout3.addWidget(self.canvas)
        self.layout3.addWidget(self.log)

        self.log.setFixedHeight(60)
