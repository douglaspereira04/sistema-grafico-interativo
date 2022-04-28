import sys
import re
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QLineEdit, QInputDialog, QDialog, QPlainTextEdit, QDialogButtonBox, QFormLayout
from PyQt5.QtGui import QPixmap, QColor, QIntValidator
from PyQt5.QtCore import Qt
from enum import Enum

class ObjType(Enum):
    POINT = 1
    LINE = 2
    WIREFRAME = 3

class Graphics:
    def __init__(self):
        self.objects = []
        self.viewport = {
            "x_max": 300, 
            "x_min": 0,
            "y_max": 300, 
            "y_min": 0
        }
        self.window = {
            "x_max": 300, 
            "x_min": 0,
            "y_max": 300, 
            "y_min": 0
        }

    def viewportTransformation(self, x, y):
        x1 = int((x- self.window["x_min"]) * (self.viewport["x_max"] - self.viewport["x_min"]) / (self.window["x_max"] - self.window["x_min"]))
        y1 = int((1 - ((y - self.window["y_min"]) / (self.window["y_max"] - self.window["y_min"]))) * (self.viewport["y_max"] - self.viewport["y_min"]))
        return (x1,y1)

class GraphicObject:
    def __init__(self, name, obj_type,coords):
        self.name = name
        self.obj_type = obj_type
        self.coords = coords

class ObjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.name = QLineEdit(self)
        self.coordinates = QPlainTextEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("Name", self.name)
        layout.addRow("Coordinates", self.coordinates)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.coordinates.setPlainText("(100,100),(200,200)")

    def getInputs(self):
        return (self.name.text(), self.coordinates.toPlainText())


class GraphicsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        ## Generate the structure parts of the MainWindow
        self.central_widget = QtWidgets.QWidget()  # A QWidget to work as Central Widget
        self.layout1 = QtWidgets.QVBoxLayout()  # Vertical Layout
        self.layout2 = QtWidgets.QHBoxLayout()  # Horizontal Layout
        self.canvas = Canvas()
        self.side_menu = SideMenu()
        # self.exitBtn = QtWidgets.QPushButton('Exit')
        ## Build the structure
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout1)
        self.layout1.addLayout(self.layout2)
        self.layout2.addWidget(self.side_menu)
        self.layout2.addWidget(self.canvas)


class Canvas(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        ##
        self.layout = QtWidgets.QVBoxLayout()  # Vertical Layout
        self.setLayout(self.layout)
        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(300, 300)
        canvas.fill(QtGui.QColor("white"))

        self.label.setPixmap(canvas)

        self.layout.addWidget(self.label)

    def clearCanvas(self):
        self.label.pixmap().fill(Qt.white)

    def drawPoint(self, x, y):

        painter = QtGui.QPainter(self.label.pixmap())
        
        painter.drawPoint(x, y)
        painter.end()
        self.label.update()

    def drawLine(self,x1,y1,x2,y2):
        global graphic

        painter = QtGui.QPainter(self.label.pixmap())

        painter.drawLine(x1, y1, x2, y2)
        painter.end()
        self.label.update()

    def draw(self, coordinates):

        if (len(coordinates) == 1):
            self.drawPoint(coordinates[0][0], coordinates[0][1])
        else:
            i=0
            while(i+1 < len(coordinates)):
                self.drawLine(coordinates[i][0], coordinates[i][1], coordinates[i+1][0], coordinates[i+1][1])
                i = i+1

            if (len(coordinates) > 2):
                self.drawLine(coordinates[i][0], coordinates[i][1], coordinates[0][0], coordinates[0][1])

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


    def makeList(self,obj_list):
        self.list.clear()
        self.list.addItems(obj_list)

class GraphicsController:
    def __init__(self, graphics, view):
        self.graphic = graphics
        self.view = view

        self.view.side_menu.zin_btn.clicked.connect(lambda: self.zoom_in())
        self.view.side_menu.zout_btn.clicked.connect(lambda: self.zoom_out())
        self.view.side_menu.add_btn.clicked.connect(lambda: self.saveObject())

        self.view.side_menu.left_btn.clicked.connect(lambda: self.pan_left())
        self.view.side_menu.right_btn.clicked.connect(lambda: self.pan_right())
        self.view.side_menu.up_btn.clicked.connect(lambda: self.pan_up())
        self.view.side_menu.down_btn.clicked.connect(lambda: self.pan_down())

        self.view.show()

    def saveObject(self):

        dialog = ObjectDialog()

        if dialog.exec():
            (name, string_coords) = dialog.getInputs()
            coords = list(eval(string_coords))

            obj_type = ObjType(3)
            if(isinstance(coords[0], int)):
                obj_type = ObjType(1)
                coords = [(coords[0], coords[1])]
            elif(len(coords)<3):
                obj_type = ObjType(2)

            obj = GraphicObject(name, obj_type, coords)
            self.graphic.objects.append(obj)

            self.draw()
            self.makeList()

    def draw(self):
        self.view.canvas.clearCanvas()
        obj_list = []
        for ob in self.graphic.objects:
            viewport_coords = [self.graphic.viewportTransformation(point[0],point[1]) for point in ob.coords]
            self.view.canvas.draw(viewport_coords)

    def makeList(self):            
        obj_list = []
        for ob in self.graphic.objects:
            obj_list.append(ob.obj_type.name + '(' + ob.name + ')')

        self.view.side_menu.makeList(obj_list)

    def resetMultiplier(self):
        if (self.view.side_menu.factor.text().strip() == ""):
            self.view.side_menu.factor.setText("10")

    def zoom_in(self):
        self.resetMultiplier()
        factor = int(self.view.side_menu.factor.text())

        self.graphic.window["x_max"] -= factor
        self.graphic.window["y_max"] -= factor
        self.draw()

    def zoom_out(self):
        self.resetMultiplier()
        factor = int(self.view.side_menu.factor.text())
        
        self.graphic.window["x_max"] += factor
        self.graphic.window["y_max"] += factor

        self.draw()


    def pan_right(self):
        self.resetMultiplier()
        factor = int(self.view.side_menu.factor.text())

        self.graphic.window["x_max"] += factor
        self.graphic.window["x_min"] += factor

        self.draw()


    def pan_left(self):
        self.resetMultiplier()
        factor = int(self.view.side_menu.factor.text())

        self.graphic.window["x_max"] -= factor
        self.graphic.window["x_min"] -= factor

        self.draw()

    def pan_up(self):
        self.resetMultiplier()
        factor = int(self.view.side_menu.factor.text())

        self.graphic.window["y_max"] -= factor
        self.graphic.window["y_min"] -= factor

        self.draw()

    def pan_down(self):
        self.resetMultiplier()
        factor = int(self.view.side_menu.factor.text())

        self.graphic.window["y_max"] += factor
        self.graphic.window["y_min"] += factor

        self.draw()

       
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    graphics = Graphics()
    window = GraphicsWindow()

    graphicsController = GraphicsController(graphics, window)

    sys.exit(app.exec_())