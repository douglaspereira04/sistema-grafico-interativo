from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

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

    def clear_canvas(self):
        self.label.pixmap().fill(Qt.white)

    def draw_point(self, x, y):

        painter = QtGui.QPainter(self.label.pixmap())
        
        painter.drawPoint(x, y)
        painter.end()
        self.label.update()

    def draw_line(self,x1,y1,x2,y2):
        global graphic

        painter = QtGui.QPainter(self.label.pixmap())

        painter.drawLine(x1, y1, x2, y2)
        painter.end()
        self.label.update()

    def draw(self, coordinates):

        if (len(coordinates) == 1):
            self.draw_point(coordinates[0][0], coordinates[0][1])
        else:
            i=0
            while(i+1 < len(coordinates)):
                self.draw_line(coordinates[i][0], coordinates[i][1], coordinates[i+1][0], coordinates[i+1][1])
                i = i+1

            if (len(coordinates) > 2):
                self.draw_line(coordinates[i][0], coordinates[i][1], coordinates[0][0], coordinates[0][1])
