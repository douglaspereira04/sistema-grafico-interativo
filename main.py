import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QLineEdit
from PyQt5.QtGui import QPixmap

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        ## Generate the structure parts of the MainWindow
        self.central_widget = QtWidgets.QWidget()  # A QWidget to work as Central Widget
        self.layout1 = QtWidgets.QVBoxLayout()  # Vertical Layout
        self.layout2 = QtWidgets.QHBoxLayout()  # Horizontal Layout
        self.widget_one = WidgetOne()
        self.widget_two = WidgetTwo()
        #self.exitBtn = QtWidgets.QPushButton('Exit')
        ## Build the structure
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout1)
        self.layout1.addLayout(self.layout2)
        self.layout2.addWidget(self.widget_two)
        self.layout2.addWidget(self.widget_one)

        ## Connect the signal
        #self.widget_one.TitleClicked.connect(self.dob_click)
        self.widget_two.ZinBtn.clicked.connect(lambda: self.on_zoom_in())
        self.widget_two.addBtn.clicked.connect(lambda: self.windowForXY())


    def windowForXY(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = WindowXY()
        self.ui.show()

    def on_zoom_in(self):
        #isso coloca no lugar especifico da tela
        #self.widget_one.setGeometry(100,100,self.widget_one.width() + 4, self.widget_one.height() + 4)
        x=1

        #size = self.widget_one.label.pixmap.size()
        #scaled_pixmap = self.widget_one.label.pixmap.scaled(size * 2)
        #self.widget_one.label.setPixmap(scaled_pixmap)

    def on_zoom_out(self):
        x=1

class WindowXY(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        ## Generate the structure parts of the MainWindow
        #Basic Structure
        self.central_widget = QtWidgets.QWidget()  # A QWidget to work as Central Widget
        self.setGeometry(20,20,200,250)
        self.textbox = QLineEdit(self)
        self.textbox.move(40,20)
        self.textbox2 = QLineEdit(self)
        self.textbox2.move(40, 60)
        self.textbox3 = QLineEdit(self)
        self.textbox3.move(40, 100)
        self.textbox4 = QLineEdit(self)
        self.textbox4.move(40, 140)
        self.button = QtWidgets.QPushButton('Add',self)
        self.button.move(40,180)
        self.labX1 = QtWidgets.QLabel('X1',self)
        self.labX1.move(20,20)
        self.labX2 = QtWidgets.QLabel('X2',self)
        self.labX2.move(20, 60)
        self.labY1 = QtWidgets.QLabel('Y1',self)
        self.labY1.move(20, 100)
        self.labY2 = QtWidgets.QLabel('Y2',self)
        self.labY2.move(20, 140)

class WidgetOne(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        ##
        self.layout = QtWidgets.QVBoxLayout()  # Vertical Layout
        self.setLayout(self.layout)
        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(300,300)
        canvas.fill(QtGui.QColor("white"))

        self.label.setPixmap(canvas)

        self.layout.addWidget(self.label)
        self.draw()

    def draw(self):
        painter = QtGui.QPainter(self.label.pixmap())
        painter.drawLine(100,100,200,200)
        painter.end()

class WidgetTwo(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.title = QtWidgets.QLabel('Menu de funções')
        self.list = QtWidgets.QListWidget()
        self.list.setMaximumWidth(100)
        self.list.setMaximumHeight(100)
        self.addBtn = QtWidgets.QPushButton('Add')
        self.leftBtn = QtWidgets.QPushButton('Left')
        self.rightBtn = QtWidgets.QPushButton('Right')
        self.upBtn = QtWidgets.QPushButton('Up')
        self.downBtn = QtWidgets.QPushButton('Down')
        self.ZinBtn = QtWidgets.QPushButton('Zoom In')
        self.ZoutBtn = QtWidgets.QPushButton('Zoom Out')
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.addBtn)
        self.layout.addWidget(self.leftBtn)
        self.layout.addWidget(self.rightBtn)
        self.layout.addWidget(self.upBtn)
        self.layout.addWidget(self.downBtn)
        self.layout.addWidget(self.ZinBtn)
        self.layout.addWidget(self.ZoutBtn)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())