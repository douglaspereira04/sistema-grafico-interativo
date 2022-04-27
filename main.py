import sys
import re
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QLineEdit, QInputDialog, QDialog, QPlainTextEdit, QDialogButtonBox, QFormLayout
from PyQt5.QtGui import QPixmap
from enum import Enum

class ObjType(Enum):
    POINT = 1
    LINE = 2
    WIREFRAME = 3

class GObject:
    def __init__(self, name, obj_type,coords):
        self.name = name
        self.obj_type = obj_type
        self.coords = coords

objects = []

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.first = QLineEdit(self)
        self.second = QPlainTextEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("Name", self.first)
        layout.addRow("Coordinates", self.second)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.second.setPlainText("(100,100),(200,200)")

    def getInputs(self):
        return (self.first.text(), self.second.toPlainText())


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
        self.ui = WindowXY()


        ## Connect the signal
        #self.widget_one.TitleClicked.connect(self.dob_click)
        self.widget_two.ZinBtn.clicked.connect(lambda: self.on_zoom_in())
        self.widget_two.addBtn.clicked.connect(lambda: self.saveValue())

    def saveValue(self):
        dialog = InputDialog()

        if dialog.exec():
            (name, string_coords) = dialog.getInputs()
            coords = list(eval(string_coords))

            obj_type = ObjType(3)
            if(isinstance(coords[0], int)):
                obj_type = ObjType(1)
            elif(len(coords)<3):
                obj_type = ObjType(2)

            obj = GObject(name, obj_type, coords)
            objects.append(obj)

            self.widget_one.draw(coords)
            
            obj_list = []
            for ob in objects:
                obj_list.append(ob.obj_type.name+'('+ob.name+')')

            self.widget_two.makeList(obj_list)



    def windowForXY(self):
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
        self.coordinates_box = QLineEdit(self)
        self.coordinates_box.move(40, 60)
        self.button = QtWidgets.QPushButton('Add',self)
        self.button.move(40,180)
        self.labX1 = QtWidgets.QLabel('Coordinates',self)
        self.labX1.move(20,20)



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

    def drawLine(self,x1,y1,x2,y2):
        painter = QtGui.QPainter(self.label.pixmap())
        painter.drawLine(x1, y1, x2, y2)
        painter.end()
        self.update()

    def draw(self, coordinates):
        i=0
        while(i+1 < len(coordinates)):
            self.drawLine(coordinates[i][0], coordinates[i][1], coordinates[i+1][0], coordinates[i+1][1])
            i = i+1

        if (len(coordinates) > 2):
            self.drawLine(coordinates[i][0], coordinates[i][1], coordinates[0][0], coordinates[0][1])




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

    def makeList(self,obj_list):
        self.list.clear()
        self.list.addItems(obj_list)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())