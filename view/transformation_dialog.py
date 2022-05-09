from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLabel
from PyQt5.QtGui import QDoubleValidator
from enum import Enum

class RotationType(Enum):
    OBJECT_CENTER = 1
    WORLD_CENTER = 2
    GIVEN_POINT = 3



class TransformationDialog(QDialog):
    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.setWindowTitle("Trasform")

        self.rotation = None
        self.scaling = None
        self.translation = None

        self.name = QLabel(name)
        self.buttonBox = None
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)



        layout = QtWidgets.QVBoxLayout(self)
        rotation_widget = QtWidgets.QWidget()
        scaling_widget = QtWidgets.QWidget()
        translation_widget = QtWidgets.QWidget()

        rotation_layout = QtWidgets.QVBoxLayout()
        scaling_layout = QtWidgets.QFormLayout()
        translation_layout = QtWidgets.QFormLayout()

        rotation_widget.setLayout(rotation_layout)
        scaling_widget.setLayout(scaling_layout)
        translation_widget.setLayout(translation_layout)


        #transformation log

        self.transformation_changes = QtWidgets.QPlainTextEdit()
        self.transformation_changes.setReadOnly(True)
        self.transformation_changes.setMaximumHeight(self.transformation_changes.font().pointSize()*10)

        #rotation center

        self.no_rotation = QtWidgets.QRadioButton('No rotation')
        self.object_center = QtWidgets.QRadioButton('Object Center')
        self.world_center = QtWidgets.QRadioButton('World Center')
        self.given_point = QtWidgets.QRadioButton('Given Point')

        rotation_layout.addWidget(self.no_rotation)
        rotation_layout.addWidget(self.object_center)
        rotation_layout.addWidget(self.world_center)
        rotation_layout.addWidget(self.given_point)

        #rotation options

        rotation_options_layout = QtWidgets.QGridLayout()
        given_x_label = QtWidgets.QLabel("x: ")
        given_y_label = QtWidgets.QLabel("y: ")
        degrees_label = QtWidgets.QLabel("degrees(º): ")

        self.given_x = QtWidgets.QLineEdit()
        self.given_y = QtWidgets.QLineEdit()
        self.degrees = QtWidgets.QLineEdit()

        self.given_x.setValidator(QDoubleValidator());
        self.given_y.setValidator(QDoubleValidator());
        self.degrees.setValidator(QDoubleValidator());

        rotation_options_layout.addWidget(given_x_label,0,0,1,1)
        rotation_options_layout.addWidget(self.given_x,0,1,1,1)
        rotation_options_layout.addWidget(given_y_label,0,2,1,1)
        rotation_options_layout.addWidget(self.given_y,0,3,1,1)
        rotation_options_layout.addWidget(degrees_label,1,0,1,1)
        rotation_options_layout.addWidget(self.degrees,1,1,1,1)


        rotation_layout.addLayout(rotation_options_layout)


        self.given_point.toggled.connect(self.given_point_toggled)
        self.world_center.toggled.connect(self.world_center_toggled)
        self.object_center.toggled.connect(self.object_center_toggled)
        self.no_rotation.toggled.connect(self.no_rotation_toggled)

        self.degrees.textChanged.connect(self.add_rotation)
        self.given_y.textChanged.connect(self.add_rotation)
        self.given_x.textChanged.connect(self.add_rotation)

        self.no_rotation.setChecked(True)
        #scaling

        self.scale = QtWidgets.QLineEdit()
        self.scale.setValidator(QDoubleValidator());
        scaling_layout.addRow("Scale(%): ", self.scale)

        self.scale.textChanged.connect(self.add_scale)

        #translation

        self.translation_x = QtWidgets.QLineEdit()
        self.translation_y = QtWidgets.QLineEdit()

        self.translation_x.setValidator(QDoubleValidator());
        self.translation_y.setValidator(QDoubleValidator());

        translation_layout.addRow("x: ", self.translation_x)
        translation_layout.addRow("y: ", self.translation_y)

        self.translation_x.textChanged.connect(self.add_translation)
        self.translation_y.textChanged.connect(self.add_translation)

        #tabs

        transform_tabs = QtWidgets.QTabWidget()
        transform_tabs.addTab(rotation_widget, "Rotation")
        transform_tabs.addTab(scaling_widget, "Scaling")
        transform_tabs.addTab(translation_widget, "Translation")

        rotation_layout.setAlignment(Qt.AlignTop)
        scaling_layout.setAlignment(Qt.AlignTop)
        translation_layout.setAlignment(Qt.AlignTop)

        #transform layout

        transform_layout = QtWidgets.QVBoxLayout()

        transform_layout.addWidget(transform_tabs)
        transform_layout.addWidget(self.transformation_changes)

        layout.addWidget(self.name)
        layout.addLayout(transform_layout)

        layout.addWidget(buttonBox)

        self.list_transformations()

    def add_rotation(self):
        center = ""
        if(self.object_center.isChecked()):
            center = RotationType.OBJECT_CENTER
        elif(self.world_center.isChecked()):
            center = RotationType.WORLD_CENTER
        elif(self.given_point.isChecked()):
            center = RotationType.GIVEN_POINT
        else:
            center = None

        if(center == None):
            self.rotation = None
        else:
            self.rotation = (center.name, self.degrees.text(), self.given_x.text(), self.given_y.text())
        self.list_transformations()

    def add_scale(self):
        if(self.scale.text() == ""):
            self.scaling = None
        else:
            self.scaling = (self.scale.text())

        self.list_transformations()

    def add_translation(self):
        if(self.translation_x.text() == "" and self.translation_y.text() == ""):
            self.translation = None
        else:
            self.translation = (self.translation_x.text(),self.translation_y.text())

        self.list_transformations()

    def list_transformations(self):
        self.transformation_changes.setPlainText("Rotation: " + str(self.rotation) + "\n" + "Scaling: " +str(self.scaling) + "\n" + "Translation: " + str(self.translation))


    def given_point_toggled(self):
        if(self.given_point.isChecked()):
            self.degrees.setReadOnly(False)
            self.given_x.setReadOnly(False)
            self.given_y.setReadOnly(False)
            self.add_rotation()

    def world_center_toggled(self):
        if(self.world_center.isChecked()):
            self.degrees.setReadOnly(False)
            self.given_x.setReadOnly(True)
            self.given_x.setText("")
            self.given_y.setReadOnly(True)
            self.given_y.setText("")
            self.add_rotation()

    def object_center_toggled(self):
        if(self.object_center.isChecked()):
            self.degrees.setReadOnly(False)
            self.given_x.setReadOnly(True)
            self.given_x.setText("")
            self.given_y.setReadOnly(True)
            self.given_y.setText("")
            self.add_rotation()

    def no_rotation_toggled(self):
        if(self.no_rotation.isChecked()):
            self.degrees.setReadOnly(True)
            self.degrees.setText("")
            self.given_x.setReadOnly(True)
            self.given_x.setText("")
            self.given_y.setReadOnly(True)
            self.given_y.setText("")
            self.add_rotation()
            
    def get_inputs(self):
        return (self.rotation, self.scaling, self.translation)