import sys
import re
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

from controller.graphics_controller import GraphicsController
from model.graphics import Graphics
from view.graphics_window import GraphicsWindow

if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        graphics = Graphics()
        window = GraphicsWindow()

        graphicsController = GraphicsController(graphics, window)

        sys.exit(app.exec_())