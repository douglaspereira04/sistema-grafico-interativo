from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLineEdit, QPlainTextEdit, QDialogButtonBox, QFormLayout

class ObjectDialog(QDialog):
    def __init__(self, parent=None, name="", coords=""):
        super().__init__(parent)

        self.name = QLineEdit(name)
        self.coordinates = QPlainTextEdit(coords)
        self.buttonBox = None


        self.name.setPlaceholderText("Name")
        self.coordinates.setPlaceholderText("(x1,y1),(x2,y2),...,(xn,yn)")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("Name", self.name)
        layout.addRow("Coordinates", self.coordinates)
        layout.addWidget(buttonBox)

    def get_inputs(self):
        return (self.name.text(), self.coordinates.toPlainText())