from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLineEdit, QPlainTextEdit, QDialogButtonBox, QFormLayout

class ObjectDialog(QDialog):
    def __init__(self, parent=None, name="", coords="", color=""):
        super().__init__(parent)

        self.name = QLineEdit(name)
        self.color = QLineEdit(color)
        self.coordinates = QPlainTextEdit(coords)
        self.buttonBox = None


        self.name.setPlaceholderText("Name")
        self.color.setPlaceholderText("Color HEX value")
        self.coordinates.setPlaceholderText("(x1,y1),(x2,y2),...,(xn,yn)")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("Name: ", self.name)
        layout.addRow("Color: ", self.color)
        layout.addRow("Coordinates: ", self.coordinates)
        layout.addWidget(buttonBox)

    def get_inputs(self):
        return (self.name.text(), self.coordinates.toPlainText(), self.color.text())