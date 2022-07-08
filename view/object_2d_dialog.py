from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLineEdit, QPlainTextEdit, QDialogButtonBox, QFormLayout, QCheckBox
import numbers
from view.util.dialogs import show_error_box

class Object2DDialog(QDialog):

    def __init__(self, parent=None, name="", coords="", color="#000000", filled=False, _type=None):
        super().__init__(parent)

        self.setWindowTitle("Object")

        self.name = QLineEdit(name)
        self.color = QLineEdit(color)
        self.filled = QCheckBox()
        self.filled.setChecked(filled)
        self.filled.setEnabled(False)
        self.coordinates = QPlainTextEdit(coords)
        self.buttonBox = None

        self._type = QtWidgets.QComboBox();
        self._type.addItem("Point")
        self._type.addItem("Line/Wireframe")
        self._type.addItem("Object (Points/Lines/Wireframes)")
        self._type.addItem("Spline")
        self._type.addItem("Bezier")

        if(_type != None):
            if(_type == "Point"):
                self._type.setCurrentIndex(0)
            elif(_type == "Line/Wireframe"):
                self._type.setCurrentIndex(1)
            elif(_type == "Object (Points/Lines/Wireframes)"):
                self._type.setCurrentIndex(2)
            elif(_type == "Spline"):
                self._type.setCurrentIndex(3)
            elif(_type == "Bezier"):
                self._type.setCurrentIndex(4)


        self.name.setPlaceholderText("Name")
        self.color.setPlaceholderText("Color HEX value")
        self.coordinates.setPlaceholderText("(x,y,z)")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("Name: ", self.name)
        layout.addRow("Color: ", self.color)
        layout.addRow("Type: ", self._type)
        layout.addRow("Filled: ", self.filled)
        layout.addRow("Coordinates: ", self.coordinates)
        layout.addWidget(buttonBox)


        self.coordinates.textChanged.connect(self.set_filled_state)
        self._type.currentTextChanged.connect(self.set_filled_state)
        self.filled.stateChanged.connect(self.set_filled_state)
        self.set_filled_state()

    def accept(self):
        _type = self._type.currentText()
        if(_type=="Point"):
            if(self.well_writen_point()):
                super().accept()
            else:
                show_error_box("Expected: (x,y)")
        elif(_type=="Bezier"):
            ok = self.well_writen_bezier() 
            if(ok == 0):
                super().accept()
            elif(ok == 1):
                show_error_box("Expected: (x0,y0),(x1,y1),(x2,y2),...,(xn,yn)")
            elif(ok == 2):
                show_error_box("Expected (number of points)%3 == 1")

        elif(_type=="Spline"):
            ok = self.well_writen_spline() 
            if(ok == 0):
                super().accept()
            elif(ok == 1):
                show_error_box("Expected: (x0,y0),(x1,y1),(x2,y2),...,(xn,yn)")
            elif(ok == 2):
                show_error_box("Expected (number of points) > 3")

        elif(_type=="Line/Wireframe"):
            if(self.well_writen_wireframe()):
                super().accept()
            else:
                show_error_box("Expected: (x0,y0),(x1,y1),...,(xn,yn)")
        elif(_type=="Object (Points/Lines/Wireframes)"):
            if(self.well_writen_object()):
                super().accept()
            else:
                show_error_box("Expected: (x00,y01),...;(x10,y11),...;...(xij,yij)")

    def get_inputs(self):
        return (self.name.text(), self.get_element_list(), self.color.text(), self.filled.isChecked(), self._type.currentText())

    def is_point(self, point):
        try:
            (x,y) = point
            are_num = isinstance(x, numbers.Number)
            are_num = are_num and isinstance(y, numbers.Number)
            return are_num
        except Exception as e:
            return False

    def get_element_list(self):
        element_list = list()
        elements_strings = self.coordinates.toPlainText().split(";")
        for element in elements_strings:
            vertex_list = list(eval(element))
            if(self.is_point(vertex_list)):
                point = tuple(vertex_list)
                vertex_list = list()
                vertex_list.append(point)
            element_list.append(vertex_list)
        return element_list

    def set_filled_state(self):
        self.enable_filled(self.can_fill())

        _type = self._type.currentText()
        if(_type=="Point"):
            self.coordinates.setPlaceholderText("(x,y,z)")
        elif(_type=="Bezier"):
            self.coordinates.setPlaceholderText("(x0,y0),(x1,y1),(x2,y2),...,(xn,yn)")
        elif(_type=="Spline"):
            self.coordinates.setPlaceholderText("(x0,y0),(x1,y1),(x2,y2),...,(xn,yn)")
        elif(_type=="Line/Wireframe"):
            self.coordinates.setPlaceholderText("(x0,y0),(x1,y1),...,(xn,yn)")
        elif(_type=="Object (Points/Lines/Wireframes)"):
            self.coordinates.setPlaceholderText("(x00,y01),...;(x10,y11),...;...(xij,yij)")



    def enable_filled(self, enabled):
        if(self.filled.isChecked() and (not enabled)):
            self.filled.setChecked(False)
        self.filled.setEnabled(enabled)
     

    def well_writen_point(self):
        try:
            element_list = self.get_element_list()
            is_one_element = len(element_list) == 1
            is_point = len(element_list[0]) == 1
            return is_one_element and is_point
        except Exception as e:
            return False

    def is_element(self,element):
        is_point_list = all(self.is_point(point) for point in element)
        return is_point_list

    def well_writen_object(self):
        try:
            element_list = self.get_element_list()
            for element in element_list:
                if(not self.is_element(element)):
                    return False
            return True
        except Exception as e:
            return False

    def well_writen_wireframe(self):
        try:
            if(self.well_writen_object()):
                element_list = self.get_element_list()
                element = element_list[0]
                is_one_element = len(element_list) == 1
                is_wireframe = len(element) > 1
                return is_one_element and is_wireframe

            return False
        except Exception as e:
            return False


    def well_writen_bezier(self):
        try:
            if(self.well_writen_object()):
                element_list = self.get_element_list()
                element = element_list[0]
                is_one_element = len(element_list) == 1
                is_bezier = len(element)%3 == 1

                if(is_one_element):
                    if (is_bezier):
                        return 0
                    return 2

            return 1
        except Exception as e:
            return 1

    def well_writen_spline(self):
        try:
            if(self.well_writen_object()):
                element_list = self.get_element_list()
                element = element_list[0]
                is_one_element = len(element_list) == 1
                is_spline = len(element)>3
                
                if( is_one_element):
                    if (is_spline):
                        return 0
                    return 2

            return 1
        except Exception as e:
            return 1

    def can_fill(self):
        try:
            element_list = self.get_element_list()
            if(self.well_writen_object() and (not self.well_writen_point())):
                for element in element_list:
                    if len(element) < 3:
                        return False
                return True
            return False
        except Exception as e:
            return False
                