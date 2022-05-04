from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal

class Canvas(QtWidgets.QLabel):
    resize = pyqtSignal(int)
    wheel_y = pyqtSignal(int)
    wheel_x = pyqtSignal(int)

    def __init__(self, min_width, min_height, bg_color):
        QtWidgets.QWidget.__init__(self)

        self.setFocusPolicy(Qt.WheelFocus)
        self.coordinates = []

        self.canvas = QtGui.QPixmap(min_width, min_height)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.canvas.fill(QtGui.QColor(bg_color))

        self.setPixmap(self.canvas)

        self.lock_size = False


    def resizeEvent(self, event):
        if(self.lock_size == False):
            self.canvas = self.canvas.scaled(self.width(), self.height())
            self.setPixmap(self.canvas)
            self.resize.emit(1)

    def draw(self, coordinates, color):
        painter = QtGui.QPainter(self.pixmap())
        painter.setPen(color)

        self.coordinates = coordinates

        if (len(coordinates) == 1):
            painter.drawPoint(coordinates[0][0], coordinates[0][1])
        else:
            i=0
            while(i+1 < len(coordinates)):
                painter.drawLine(coordinates[i][0], coordinates[i][1], coordinates[i+1][0], coordinates[i+1][1])
                i = i+1

            if (len(coordinates) > 2):
                painter.drawLine(coordinates[i][0], coordinates[i][1], coordinates[0][0], coordinates[0][1])
        painter.end()