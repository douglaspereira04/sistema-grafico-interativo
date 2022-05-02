from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QPlainTextEdit, QAction, QComboBox, QLineEdit
from PyQt5.QtGui import QIntValidator
from view.canvas import Canvas
from view.side_menu import SideMenu

class GraphicsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        ## Generate the structure parts of the MainWindow
        self.central_widget = QtWidgets.QWidget()  # A QWidget to work as Central Widget
        self.right_widget = QtWidgets.QWidget()  # A QWidget to work as Central Widget
        self.layout1 = QtWidgets.QVBoxLayout()  # Vertical Layout
        self.main_layout = QtWidgets.QHBoxLayout()  # Horizontal Layout
        self.canvas_layout = QtWidgets.QVBoxLayout()  # Vorizontal Layout
        self.canvas_control_layout = QtWidgets.QHBoxLayout()  # Vorizontal Layout
        self.canvas = Canvas(300,300)
        self.log = QPlainTextEdit(self)
        self.log.setReadOnly(True)

        self.side_menu = SideMenu()
        # self.exitBtn = QtWidgets.QPushButton('Exit')
        ## Build the structure
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout1)
        self.layout1.addLayout(self.main_layout)
        self.main_layout.addWidget(self.side_menu)
        self.main_layout.addLayout(self.canvas_layout)

        self.canvas_layout.addLayout(self.canvas_control_layout)
        self.canvas_layout.addWidget(self.canvas)
        self.canvas_layout.addWidget(self.log)

        self.viewport_label = QtWidgets.QLabel('Viewport')

        font = self.viewport_label.font()
        size = font.pointSize()
        self.viewport_label.setMaximumHeight(size+10)
        self.canvas_control_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.canvas_control_layout.addWidget(self.viewport_label)




        self.log.setFixedHeight(60)

        self.load_from_file = QAction('Load from file', self)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(self.load_from_file)

