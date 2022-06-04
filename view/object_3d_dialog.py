from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLineEdit, QPlainTextEdit, QDialogButtonBox, QFormLayout, QCheckBox
import numbers
from model.graphic_3d_object import Object3d



class Object3dDialog(QDialog):
    def __init__(self, parent=None, name="", vertices="", edges="", color=""):
        super().__init__(parent)

        self.setWindowTitle("Object")

        self.name = QLineEdit(name)
        self.color = QLineEdit(color)
        self.vertices = QPlainTextEdit(vertices)
        self.edges = QPlainTextEdit(edges)
        self.buttonBox = None


        self.name.setPlaceholderText("Name")
        self.color.setPlaceholderText("Color HEX value")
        self.vertices.setPlaceholderText("(x1,y1,z1),(x2,y2,z2),...,(xn,yn,zn)")
        self.edges.setPlaceholderText("(vi,vj),(vk,vl),...,(vn,vm)")

        self.name.setText("A")
        self.color.setText("#000000")
        self.vertices.setPlainText("(1,2,3),(2,3,4)")
        self.edges.setPlainText("(0,1)")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("Name: ", self.name)
        layout.addRow("Color: ", self.color)
        layout.addRow("Vertices: ", self.vertices)
        layout.addRow("Edges: ", self.edges)
        layout.addWidget(buttonBox)

    def get_obj(self):
        return Object3d.from_string(self.name.text(),self.vertices.toPlainText(),self.edges.toPlainText(),self.color.text())

