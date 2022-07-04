from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QResizeEvent

class Canvas(QtWidgets.QLabel):
    resize = pyqtSignal(QResizeEvent)
    zoom = pyqtSignal(int)

    pan = pyqtSignal(int)

    rotate_xy_window = pyqtSignal(int)
    rotate_z_window = pyqtSignal(int)

    grab = pyqtSignal(int)
    rotate = pyqtSignal(int)
    scale = pyqtSignal(int)


    def __init__(self, min_width, min_height, bg_color):
        QtWidgets.QWidget.__init__(self)

        self.setFocusPolicy(Qt.WheelFocus)
        self.coordinates = []

        self.canvas = QtGui.QPixmap(min_width, min_height)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.canvas.fill(QtGui.QColor(bg_color))

        self.setPixmap(self.canvas)

        self.lock_size = False

        self.wheel_y_angle = 0
        self.last_mouse_pos = None
        self.current_mouse_pos = None

        self.grab_enabled = False
        self.rotate_enabled = False
        self.scale_enabled = False


    def resizeEvent(self, event):
        if(self.lock_size == False):
            self.canvas = self.canvas.scaled(self.width(), self.height())
            self.setPixmap(self.canvas)
            self.resize.emit(event)

    def get_painter(self):
        return QtGui.QPainter(self.pixmap())

    def draw(self, coordinates, color, filled=False, line_set=False):
        painter = QtGui.QPainter(self.pixmap())
        painter.setPen(color)

        length = len(coordinates)

        if(line_set):
            for ((x0,y0), (x1,y1)) in coordinates:
                painter.drawLine(x0,y0,x1,y1)
        elif (length == 1):
            painter.drawPoint(coordinates[0][0], coordinates[0][1])
        elif(length < 3 or (not filled)):
            i=0
            while(i+1 < len(coordinates)):
                painter.drawLine(coordinates[i][0], coordinates[i][1], coordinates[i+1][0], coordinates[i+1][1])
                i = i+1
        else:
            painter.setBrush(QtGui.QBrush(color))
         
            vertices = [QPoint(x,y) for (x,y) in coordinates] 
            polygon = QtGui.QPolygon(vertices)
         
            painter.drawPolygon(polygon)


        painter.end()

    def drawPolygon(self, coordinates, color):
        painter = QPainter(self.pixmap())
        painter.setPen(color)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            modifiers = QApplication.keyboardModifiers()
            self.last_mouse_pos = self.current_mouse_pos
            self.current_mouse_pos = event.localPos()


            if(self.grab_enabled):
                self.grab.emit(1)
            elif(self.rotate_enabled):
                self.rotate.emit(1)
            elif(self.scale_enabled):
                self.scale.emit(1)

            elif modifiers == (Qt.ControlModifier):
                self.rotate_z_window.emit(1)

            elif modifiers == (Qt.AltModifier | Qt.ShiftModifier):
                self.pan.emit(1)

            elif modifiers == (Qt.ShiftModifier):
                self.rotate_xy_window.emit(1)


        super().mouseMoveEvent(event)



    def wheelEvent(self, event):
        angle = event.angleDelta()

        modifiers = QApplication.keyboardModifiers()
        self.zoom.emit(angle.y())
        self.wheel_y_angle = angle.y()

        super().wheelEvent(event)

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_G):
            self.grab_enabled = True
        elif (event.key() == Qt.Key_R):
            self.rotate_enabled = True
        elif (event.key() == Qt.Key_S):
            self.scale_enabled = True
        super().keyReleaseEvent(event)


    def keyReleaseEvent(self, event):
        if (event.key() == Qt.Key_G or event.key() == Qt.Key_R or event.key() == Qt.Key_S):
            self.grab_enabled = False
            self.rotate_enabled = False
            self.scale_enabled = False


        self.last_mouse_pos = None
        self.current_mouse_pos = None

        super().keyReleaseEvent(event)

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None
        self.current_mouse_pos = None
        super().mouseReleaseEvent(event)

    def get_mouse_movement(self):
        x_diff = 0
        y_diff = 0
        if(self.current_mouse_pos != None and self.last_mouse_pos != None):
            x_diff = self.current_mouse_pos.x() - self.last_mouse_pos.x()
            y_diff = self.current_mouse_pos.y() - self.last_mouse_pos.y()

        return (x_diff, y_diff)