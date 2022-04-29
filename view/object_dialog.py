from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLineEdit, QPlainTextEdit, QDialogButtonBox, QFormLayout

class ObjectDialog(QDialog):
    def __init__(self, parent=None, name="", coords="", is_new=True):
        super().__init__(parent)

        self.name = QLineEdit(self)
        self.coordinates = QPlainTextEdit(self)
        self.buttonBox = None
        self.delete = False
        if (is_new):
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)
        else:
            buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Discard | QDialogButtonBox.Cancel, self);
            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)
            buttonBox.button(QDialogButtonBox.Discard).setText("Delete");
            buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.set_delete)

        layout = QFormLayout(self)
        layout.addRow("Name", self.name)
        layout.addRow("Coordinates", self.coordinates)
        layout.addWidget(buttonBox)

        self.name.setText("A")
        self.coordinates.setPlainText("(100,100),(200,200)")

    def get_inputs(self):
        return (self.name.text(), self.coordinates.toPlainText(), self.delete)
    
    def set_delete(self):
        self.delete = True
        self.accept()