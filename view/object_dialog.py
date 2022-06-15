from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLineEdit, QPlainTextEdit, QDialogButtonBox, QFormLayout, QCheckBox
import numbers

class ObjectDialog(QDialog):
    def __init__(self, parent=None, name="A", coords="(0,0,0),(0,50,0),(0,0,0),(50,0,0),(0,0,0),(0,0,50),(0,50,0),(0,50,50),(0,50,50),(0,0,50),(0,0,50),(50,0,50),(50,0,50),(50,0,0),(50,0,0),(50,50,0),(50,50,0),(0,50,0),(50,50,0),(50,50,50),(50,50,50),(0,50,50)", color="#FF0000", filled=False, bezier=False, spline=False):
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

        self.spline = QCheckBox()
        self.spline.setChecked(spline)
        self.spline.setEnabled(False)


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


        self.coordinates.textChanged.connect(self.set_filled_state)
        self.bezier.stateChanged.connect(self.set_filled_state)
        self.spline.stateChanged.connect(self.set_filled_state)
        self.filled.stateChanged.connect(self.set_filled_state)
        self.set_filled_state()

    def get_inputs(self):
        return (self.name.text(), self.coordinates.toPlainText(), self.color.text(), self.filled.isChecked(), self.bezier.isChecked(), self.spline.isChecked())

    def set_filled_state(self):

        try:
            obj_list = list(eval(self.coordinates.toPlainText()))
            well_written = all(isinstance(x, numbers.Number) and isinstance(y, numbers.Number) and isinstance(z, numbers.Number) for (x,y,z) in obj_list)

            if(well_written and len(obj_list)>2):
                self.enable_filled(True)
            else:
                self.enable_filled(False)

            if(well_written and (len(obj_list)%3 == 1) and (not self.spline.isChecked())):
                self.enable_bezier(True)
            else:
                self.enable_bezier(False)


            if(well_written and len(obj_list)>3 and (not self.bezier.isChecked())):
                self.enable_spline(True)
            else:
                self.enable_spline(False)

        except Exception as e:
            self.enable_filled(False)
            self.enable_bezier(False)


    def enable_filled(self, enabled):
        if(self.filled.isChecked() and (not enabled)):
            self.filled.setChecked(False)
        self.filled.setEnabled(enabled)
        

    def enable_bezier(self, enabled):
        self.bezier.setEnabled(enabled)
        if(self.bezier.isChecked() and (not enabled)):
            self.bezier.setChecked(False)

    def enable_spline(self, enabled):
        self.spline.setEnabled(enabled)
        if(self.spline.isChecked() and (not enabled)):
            self.spline.setChecked(False)
        


