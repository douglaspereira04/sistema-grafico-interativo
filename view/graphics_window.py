from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QPlainTextEdit, QAction,QActionGroup, QComboBox, QLineEdit
from PyQt5.QtGui import QIntValidator, QFont
from view.canvas import Canvas
from view.side_menu import SideMenu

class GraphicsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.setFont(QFont('Arial', 10))

        self.setWindowTitle("Computação Gráfica")
        ## Generate the structure parts of the MainWindow
        self.central_widget = QtWidgets.QWidget()  # A QWidget to work as Central Widget
        self.right_widget = QtWidgets.QWidget()  # A QWidget to work as Central Widget
        self.layout1 = QtWidgets.QVBoxLayout()  # Vertical Layout
        self.main_layout = QtWidgets.QHBoxLayout()  # Horizontal Layout
        self.canvas_layout = QtWidgets.QVBoxLayout()  # Vorizontal Layout
        self.canvas_control_layout = QtWidgets.QHBoxLayout()  # Vorizontal Layout
        self.canvas = Canvas(256,256, "white")
        self.log = QPlainTextEdit(self)
        self.log.setReadOnly(True)

        self.side_menu = SideMenu(150)
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




        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('File')
        self.load_from_file = QAction('Load from file', self)
        self.save_to_file = QAction('Save to file', self)

        file_menu.addAction(self.load_from_file)
        file_menu.addAction(self.save_to_file)

        clipping_menu = menu_bar.addMenu('Clipping')
        self.enable_clipping = QAction('Clip', self)
        self.enable_clipping.setCheckable(True);
        self.enable_clipping.setChecked(True);
        
        self.lian_barsk = QAction('Lian-Barsk Line Clipping', self)
        self.lian_barsk.setCheckable(True);
        self.lian_barsk.setChecked(True);
        self.cohen_sutherland = QAction('Cohen-Sutherland Line Clipping', self)
        self.cohen_sutherland.setCheckable(True);


        self.line_clipping_group = QActionGroup(self);
        self.line_clipping_group.addAction(self.lian_barsk);
        self.line_clipping_group.addAction(self.cohen_sutherland);
        self.line_clipping_group.setExclusive(True)

        clipping_menu.addAction(self.enable_clipping)
        clipping_menu.addAction(self.lian_barsk)
        clipping_menu.addAction(self.cohen_sutherland)

        #test_menu = menu_bar.addMenu('Test')
        self.test_normalization = QAction('Normalization Demonstration', self)

        #test_menu.addAction(self.test_normalization)



        #test_menu.setFont(QFont('Arial', 10))
        clipping_menu.setFont(QFont('Arial', 10))
        file_menu.setFont(QFont('Arial', 10))
    def set_canvas_color(self, color):
        self.canvas.canvas.fill(QtGui.QColor(color))

