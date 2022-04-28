import sys
import re
from PyQt5 import QtGui, QtCore, QtWidgets
<<<<<<< HEAD
from PyQt5.QtWidgets import QApplication, QLineEdit, QInputDialog, QDialog, QPlainTextEdit, QDialogButtonBox, QFormLayout
=======
from PyQt5.QtWidgets import QApplication, QLineEdit, QInputDialog, QDialog, QPlainTextEdit, QDialogButtonBox, \
    QFormLayout
>>>>>>> 945d9ede193ece437c3df2618dda89f7c19c5e5f
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
from enum import Enum

<<<<<<< HEAD
=======

>>>>>>> 945d9ede193ece437c3df2618dda89f7c19c5e5f
class ObjType(Enum):
    POINT = 1
    LINE = 2
    WIREFRAME = 3

<<<<<<< HEAD
class GObject:
    def __init__(self, name, obj_type,coords):
=======

class GObject:
    def __init__(self, name, obj_type, coords):
>>>>>>> 945d9ede193ece437c3df2618dda89f7c19c5e5f
        self.name = name
        self.obj_type = obj_type
        self.coords = coords

<<<<<<< HEAD
=======

>>>>>>> 945d9ede193ece437c3df2618dda89f7c19c5e5f
x_vpmax = 300
x_vpmin = 0
y_vpmax = 300
y_vpmin = 0

x_wmax = 300
x_wmin = 0
y_wmax = 300
y_wmin = 0

<<<<<<< HEAD

objects = []

=======
objects = []


>>>>>>> 945d9ede193ece437c3df2618dda89f7c19c5e5f
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
        # self.exitBtn = QtWidgets.QPushButton('Exit')
        ## Build the structure
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout1)
        self.layout1.addLayout(self.layout2)
        self.layout2.addWidget(self.widget_two)
        self.layout2.addWidget(self.widget_one)
        self.ui = WindowXY()

        ## Connect the signal
        # self.widget_one.TitleClicked.connect(self.dob_click)
        self.widget_two.ZinBtn.clicked.connect(lambda: self.on_zoom_in())
        self.widget_two.ZoutBtn.clicked.connect(lambda: self.on_zoom_out())
        self.widget_two.addBtn.clicked.connect(lambda: self.saveValue())

        self.widget_two.leftBtn.clicked.connect(lambda: self.pan_left())
        self.widget_two.rightBtn.clicked.connect(lambda: self.pan_right())
        self.widget_two.upBtn.clicked.connect(lambda: self.pan_up())
        self.widget_two.downBtn.clicked.connect(lambda: self.pan_down())

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

            self.drawEverything()
            self.makeList()

    def drawEverything(self):
        self.widget_one.clearDraw()
        obj_list = []
        for ob in objects:
            if(ob.obj_type != ObjType.POINT):
                self.widget_one.draw(ob.coords)
            else:
                self.widget_one.drawP(ob.coords)

    def makeList(self):
        obj_list = []
        for ob in objects:
            obj_list.append(ob.obj_type.name + '(' + ob.name + ')')

        self.widget_two.makeList(obj_list)

    def windowForXY(self):
        self.ui.show()

    def on_zoom_in(self):
        global x_wmax
        global y_wmax
        x_wmax = x_wmax -1
        y_wmax = y_wmax -1
        self.drawEverything()

    def on_zoom_out(self):
        global x_wmax
        global y_wmax
        x_wmax = x_wmax +1
        y_wmax = y_wmax +1
        self.drawEverything()


    def pan_right(self):
        global x_wmax
        global x_wmin
        x_wmax = x_wmax +1
        x_wmin = x_wmin +1
        self.drawEverything()


    def pan_left(self):
        global x_wmax
        global x_wmin
        x_wmax = x_wmax -1
        x_wmin = x_wmin -1
        self.drawEverything()

    def pan_up(self):
        global y_wmax
        global y_wmin
        y_wmax = y_wmax -1
        y_wmin = y_wmin -1
        self.drawEverything()

    def pan_down(self):
        global y_wmax
        global y_wmin
        y_wmax = y_wmax +1
        y_wmin = y_wmin +1
        self.drawEverything()

class WindowXY(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        ## Generate the structure parts of the MainWindow
        # Basic Structure
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
        canvas = QtGui.QPixmap(300, 300)
        canvas.fill(QtGui.QColor("white"))

        self.label.setPixmap(canvas)

        self.layout.addWidget(self.label)

    def clearDraw(self):
        self.label.pixmap().fill(Qt.white)

    def drawP(self, coordinates):
        painter = QtGui.QPainter(self.label.pixmap())
        x1vp = int((coordinates[0] - x_wmin) * (x_vpmax - x_vpmin) / (x_wmax - x_wmin))
        y1vp = int((1 - ((coordinates[1] - y_wmin) / (y_wmax - y_wmin))) * (y_vpmax - y_vpmin))

        painter.drawPoint(x1vp, y1vp)
        painter.end()
        self.label.update()

    def drawLine(self,x1,y1,x2,y2):
        painter = QtGui.QPainter(self.label.pixmap())

        global x_wmax
        global y_wmax
        global x_wmin
        global y_wmin
        global x_vpmax
        global y_vpmax
        global x_vpmin
        global y_vpmin
        x1vp = int( (x1 - x_wmin)*(x_vpmax - x_vpmin)/(x_wmax - x_wmin) )
        x2vp = int( (x2 - x_wmin)*(x_vpmax - x_vpmin)/(x_wmax - x_wmin) )
        y1vp = int( (1 - ( (y1 - y_wmin) / (y_wmax - y_wmin) ) )*(y_vpmax - y_vpmin) )
        y2vp = int( (1 - ( (y2 - y_wmin) / (y_wmax - y_wmin) ) )*(y_vpmax - y_vpmin) )

        painter.drawLine(x1vp, y1vp, x2vp, y2vp)
        painter.end()
        self.label.update()

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
        self.factor = QLineEdit()
        self.factor.setPlaceholderText("Navigation multiplier");
        self.leftBtn = QtWidgets.QPushButton('Left')
        self.rightBtn = QtWidgets.QPushButton('Right')
        self.upBtn = QtWidgets.QPushButton('Up')
        self.downBtn = QtWidgets.QPushButton('Down')
        self.ZinBtn = QtWidgets.QPushButton('Zoom In')
        self.ZoutBtn = QtWidgets.QPushButton('Zoom Out')
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.addBtn)
        self.layout.addWidget(self.factor)
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