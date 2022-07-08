import sys
import re
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

from controller.graphics_3d_controller import Graphics3DController
from controller.graphics_2d_controller import Graphics2DController
from model.graphics_3d.graphics_3d import Graphics3D
from model.graphics_2d.graphics_2d import Graphics2D
from view.graphics_window import GraphicsWindow

if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        graphics = Graphics3D()
        window = GraphicsWindow()

        graphicsController = Graphics3DController(graphics, window)

        sys.exit(app.exec_())