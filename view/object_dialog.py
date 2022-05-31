from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLineEdit, QPlainTextEdit, QDialogButtonBox, QFormLayout, QCheckBox
import numbers

class ObjectDialog(QDialog):
    def __init__(self, parent=None, name="", coords="", color="", filled=False, bezier=False):
        super().__init__(parent)

        self.setWindowTitle("Object")

        self.name = QLineEdit(name)
        self.color = QLineEdit(color)
        self.filled = QCheckBox()
        self.filled.setChecked(filled)
        self.filled.setEnabled(False)
        self.coordinates = QPlainTextEdit(coords)
        self.buttonBox = None

        self.bezier = QCheckBox()
        self.bezier.setChecked(bezier)
        self.bezier.setEnabled(False)


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
        layout.addRow("Filled: ", self.filled)
        layout.addRow("Bezier Curve: ", self.bezier)


        self.coordinates.textChanged.connect(self.set_filled_state)
        self.bezier.stateChanged.connect(self.set_filled_state)
        self.filled.stateChanged.connect(self.set_filled_state)
        self.set_filled_state()

    def get_inputs(self):
        return (self.name.text(), self.coordinates.toPlainText(), self.color.text(), self.filled.isChecked(), self.bezier.isChecked())

    def set_filled_state(self):

        try:
            obj_list = list(eval(self.coordinates.toPlainText()))
            if(len(obj_list)>2 and all(isinstance(x, numbers.Number) and isinstance(y, numbers.Number) for (x,y) in obj_list)):
                self.filled.setEnabled(True)
                self.bezier.setEnabled(True)
            else:
                self.filled.setChecked(False)
                self.filled.setEnabled(False)
                self.bezier.setChecked(False)
                self.bezier.setEnabled(False)
        except Exception as e:
            self.filled.setChecked(False)
            self.filled.setEnabled(False)
            self.bezier.setChecked(False)
            self.bezier.setEnabled(False)

        if(self.bezier.isChecked()):
            self.filled.setChecked(False)
            self.filled.setEnabled(False)

        if(self.filled.isChecked()):
            self.bezier.setChecked(False)
            self.bezier.setEnabled(False)


