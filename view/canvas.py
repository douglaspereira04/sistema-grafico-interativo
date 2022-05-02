from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal

class Canvas(QtWidgets.QLabel):
    resize = pyqtSignal(int)

    def __init__(self, min_width, min_height):
        QtWidgets.QWidget.__init__(self)

        self.coordinates = []

        self.canvas = QtGui.QPixmap(min_width, min_height)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.canvas.fill(QtGui.QColor("white"))

        self.setPixmap(self.canvas)

        self.lock_size = False


    def resizeEvent(self, event):
        if(self.lock_size == False):
            self.canvas = self.canvas.scaled(self.width(), self.height())
            self.setPixmap(self.canvas)
            self.resize.emit(1)

    def draw_point(self, x, y, painter):
        painter.drawPoint(x, y)

    def draw_line(self,x1,y1,x2,y2, painter):
        painter.drawLine(x1, y1, x2, y2)

    def draw(self, coordinates, color):
        painter = QtGui.QPainter(self.pixmap())
        painter.setPen(color)

        self.coordinates = coordinates

        if (len(coordinates) == 1):
            self.draw_point(coordinates[0][0], coordinates[0][1], painter)
        else:
            i=0
            while(i+1 < len(coordinates)):
                self.draw_line(coordinates[i][0], coordinates[i][1], coordinates[i+1][0], coordinates[i+1][1], painter)
                i = i+1

            if (len(coordinates) > 2):
                self.draw_line(coordinates[i][0], coordinates[i][1], coordinates[0][0], coordinates[0][1], painter)
        painter.end()

    def erase(self, coordinates):
        self.draw(coordinates, Qt.white)