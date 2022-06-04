import sys
import re
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

from controller.graphics_3d_controller import Graphics3dController
from model.graphics_3d import Graphics3d
from view.graphics_window import GraphicsWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    graphics = Graphics3d()
    window = GraphicsWindow()

    graphicsController = Graphics3dController(graphics, window)

    sys.exit(app.exec_())