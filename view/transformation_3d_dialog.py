from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLabel, QMessageBox
from PyQt5.QtGui import QDoubleValidator
from enum import Enum
from view.util.dialogs import show_error_box

class TransformationType(Enum):
    TRANSLATION = 1
    SCALING = 2
    ROTATION = 3

class RotationType(Enum):
    OBJECT_CENTER = 1
    WORLD_CENTER = 2
    GIVEN_POINT = 3


class Transformation3dDialog(QDialog):
    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.setWindowTitle("Trasform")
        self.transformation_list = []

        self.name = QLabel(name)
        self.buttonBox = None
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)



        layout = QtWidgets.QVBoxLayout(self)
        rotation_widget = QtWidgets.QWidget()
        scaling_widget = QtWidgets.QWidget()
        translation_widget = QtWidgets.QWidget()

        rotation_layout = QtWidgets.QFormLayout()
        scaling_layout = QtWidgets.QFormLayout()
        translation_layout = QtWidgets.QFormLayout()

        rotation_widget.setLayout(rotation_layout)
        scaling_widget.setLayout(scaling_layout)
        translation_widget.setLayout(translation_layout)


        #transformation log
        transformation_list_layout = QtWidgets.QVBoxLayout()
        self.transformation_changes = QtWidgets.QListWidget()
        self.remove_transformation_btn = QtWidgets.QPushButton("Remove")

        transformation_list_layout.addWidget(self.transformation_changes)
        transformation_list_layout.addWidget(self.remove_transformation_btn)


        self.remove_transformation_btn.clicked.connect(self.delete_transformation)

        #rotation center

        self.object_center = QtWidgets.QRadioButton('Object Center')
        self.world_center = QtWidgets.QRadioButton('World Center')
        self.given_point = QtWidgets.QRadioButton('Given Point')

        rotation_layout.addRow(self.object_center)
        rotation_layout.addRow(self.world_center)
        rotation_layout.addRow(self.given_point)

        #rotation options

        self.given_x = QtWidgets.QLineEdit()
        self.given_y = QtWidgets.QLineEdit()
        self.given_z = QtWidgets.QLineEdit()
        self.degrees = QtWidgets.QLineEdit()

        self.given_x.setValidator(QDoubleValidator());
        self.given_y.setValidator(QDoubleValidator());
        self.degrees.setValidator(QDoubleValidator());

        self.axis = QtWidgets.QComboBox();
        self.axis.addItem("X")
        self.axis.addItem("Y")
        self.axis.addItem("Z")
        rotation_layout.addRow("Axis: ",self.axis)
        rotation_layout.addRow("x: ",self.given_x)
        rotation_layout.addRow("y: ",self.given_y)
        rotation_layout.addRow("z: ",self.given_z)
        rotation_layout.addRow("degrees(º): ", self.degrees)

        self.add_rotation_btn = QtWidgets.QPushButton("Add Rotation")



        self.given_point.toggled.connect(self.given_point_toggled)
        self.world_center.toggled.connect(self.world_center_toggled)
        self.object_center.toggled.connect(self.object_center_toggled)

        self.add_rotation_btn.clicked.connect(self.add_rotation)

        self.object_center.setChecked(True)

        rotation_layout.addRow(self.add_rotation_btn)
        #scaling

        self.scale = QtWidgets.QLineEdit()
        self.scale.setValidator(QDoubleValidator());

        self.add_scaling_btn = QtWidgets.QPushButton("Add Scaling")

        scaling_layout.addRow("Scale(%): ", self.scale)
        scaling_layout.addRow(self.add_scaling_btn)

        self.add_scaling_btn.clicked.connect(self.add_scale)


        #translation

        self.translation_x = QtWidgets.QLineEdit()
        self.translation_y = QtWidgets.QLineEdit()
        self.translation_z = QtWidgets.QLineEdit()
        self.add_translation_btn = QtWidgets.QPushButton("Add Translation")

        self.translation_x.setValidator(QDoubleValidator());
        self.translation_y.setValidator(QDoubleValidator());
        self.translation_z.setValidator(QDoubleValidator());

        translation_layout.addRow("x: ", self.translation_x)
        translation_layout.addRow("y: ", self.translation_y)
        translation_layout.addRow("z: ", self.translation_z)
        translation_layout.addRow(self.add_translation_btn)

        self.add_translation_btn.clicked.connect(self.add_translation)



        #tabs

        transform_tabs = QtWidgets.QTabWidget()
        transform_tabs.addTab(rotation_widget, "Rotation")
        transform_tabs.addTab(scaling_widget, "Scaling")
        transform_tabs.addTab(translation_widget, "Translation")

        transform_tabs.setMaximumWidth(300)

        rotation_layout.setAlignment(Qt.AlignTop)
        scaling_layout.setAlignment(Qt.AlignTop)
        translation_layout.setAlignment(Qt.AlignTop)

        #transform layout

        transform_layout = QtWidgets.QHBoxLayout()

        transform_layout.addWidget(transform_tabs)

        transform_layout.addLayout(transformation_list_layout)

        layout.addWidget(self.name)
        layout.addLayout(transform_layout)

        layout.addWidget(buttonBox)

        self.list_transformations()

    def add_rotation(self):
        center = None
        if(self.object_center.isChecked()):
            center = RotationType.OBJECT_CENTER
        elif(self.world_center.isChecked()):
            center = RotationType.WORLD_CENTER
        elif(self.given_point.isChecked()):
            center = RotationType.GIVEN_POINT

        rotation = None
        float_degrees = 0
        try:
            float_degrees = float(self.degrees.text())
        except ValueError:
            self.show_error_box("Invalid degrees value")
            return

        if(center == RotationType.GIVEN_POINT):
            try:
                float_given_x = float(self.given_x.text())
                float_given_y = float(self.given_y.text())
                float_given_z = float(self.given_z.text())
            except ValueError:
                self.show_error_box("Invalid point value")
                return

            rotation = (center.name, float_degrees, float_given_x, float_given_y, float_given_z, self.axis.currentText())
        else:
            rotation = (center.name, float_degrees, 0, 0, 0,  self.axis.currentText())

        self.transformation_list.append((TransformationType.ROTATION, rotation))
        self.list_transformations()

    def add_scale(self):
        try:
            scaling = float(self.scale.text())
        except ValueError:
            self.show_error_box("Invalid scale value")
            return

        self.transformation_list.append((TransformationType.SCALING, (scaling*0.01)))
        self.list_transformations()

    def add_translation(self):
        try:
            translation_x = float(self.translation_x.text())
            translation_y = float(self.translation_y.text())
            translation_z = float(self.translation_z.text())
        except ValueError:
            self.show_error_box("Invalid point value")
            return

        translation = (translation_x,translation_y, translation_z)
        self.transformation_list.append((TransformationType.TRANSLATION, translation))
        self.list_transformations()

    def list_transformations(self):
        self.transformation_changes.clear()
        display_list = [t[0].name+": "+str(t[1]) for t in self.transformation_list]
        self.transformation_changes.addItems(display_list)


    def delete_transformation(self):
        selected = self.transformation_changes.currentRow()
        if(selected != -1):
            del self.transformation_list[selected]

        self.list_transformations()

    def given_point_toggled(self):
        if(self.given_point.isChecked()):
            self.degrees.setReadOnly(False)
            self.given_x.setReadOnly(False)
            self.given_y.setReadOnly(False)
            self.given_z.setReadOnly(False)

    def world_center_toggled(self):
        if(self.world_center.isChecked()):
            self.degrees.setReadOnly(False)
            self.given_x.setReadOnly(True)
            self.given_x.setText("")
            self.given_y.setReadOnly(True)
            self.given_y.setText("")
            self.given_z.setReadOnly(True)
            self.given_z.setText("")

    def object_center_toggled(self):
        if(self.object_center.isChecked()):
            self.degrees.setReadOnly(False)
            self.given_x.setReadOnly(True)
            self.given_x.setText("")
            self.given_y.setReadOnly(True)
            self.given_y.setText("")
            self.given_z.setReadOnly(True)
            self.given_z.setText("")

    def get_transformations(self):
        return self.transformation_list