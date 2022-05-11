from view.object_dialog import ObjectDialog
from view.transformation_dialog import TransformationDialog
from model.graphic_object import GraphicObject
from model.graphics import TransformationType, RotationType
from model.obj_type import ObjType
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from view.util.dialogs import show_warning_box
import math


class GraphicsController:
    def __init__(self, graphics, view):
        self.graphic = graphics
        self.view = view

        self.view.side_menu.zin_btn.clicked.connect(self.zoom_in)
        self.view.side_menu.zout_btn.clicked.connect(self.zoom_out)
        self.view.side_menu.add_btn.clicked.connect(self.save_object)
        self.view.side_menu.edit_btn.clicked.connect(self.edit_object)
        self.view.side_menu.remove_btn.clicked.connect(self.remove_object)
        self.view.side_menu.transform_btn.clicked.connect(self.transform_object)

        self.view.side_menu.left_btn.clicked.connect(self.pan_left)
        self.view.side_menu.right_btn.clicked.connect(self.pan_right)
        self.view.side_menu.up_btn.clicked.connect(self.pan_up)
        self.view.side_menu.down_btn.clicked.connect(self.pan_down)


        self.view.show()

        self.reset_window_viewport_state()

        self.view.canvas.resize.connect(self.on_window_resize)

        self.bg_color = Qt.white
        self.line_color = Qt.black

        self.view.set_canvas_color(self.bg_color)

        self.view.load_from_file.triggered.connect(self.load_from_file)
        self.view.save_to_file.triggered.connect(self.save_to_file)

        self.view.side_menu.list.currentRowChanged.connect(self.list_selected)
        self.set_enable_object_options(False)


    def list_selected(self):
        if(self.view.side_menu.list.currentRow() >= 0):
            self.set_enable_object_options(True)
        else:
            self.set_enable_object_options(False)

    def set_enable_object_options(self, enabled):
        self.view.side_menu.transform_btn.setEnabled(enabled)
        self.view.side_menu.remove_btn.setEnabled(enabled)


    def load_from_file(self):
        self.erase()

        file_name = QFileDialog.getOpenFileName(self.view, 'Open file', '',"Text files (*.txt)")

        try:
            if(file_name[0]!=''):
                f = open(file_name[0], "r")
                data = f.read()
                f.close()
                
                self.read_graphics_data(data)

                self.draw()
                self.make_list()
        except:
            show_warning_box("Unable to load file")



    def save_to_file(self):
        file_name = QFileDialog.getSaveFileName(self.view, 'Save file', '',"Text files (*.txt)")

        try:
            if(file_name[0]!=''):
                f = open(file_name[0], "w")
                f.write(str(self.compile_graphics_data()))
                f.close()
        except:
            show_warning_box("Unable to save file")
            

    def read_graphics_data(self, data):
        obj_list = list(eval(data))


        new_objects = []

        for obj_string in obj_list:

            obj_type = ObjType[obj_string[0]]
            name = obj_string[1]
            coords = obj_string[2]
            color = obj_string[3]

            obj = GraphicObject(name, obj_type, coords, color)
            new_objects.append(obj)

        self.graphic.objects = new_objects

    def compile_graphics_data(self):
        return [(obj.obj_type.name, obj.name, obj.coords, obj.color) for obj in self.graphic.objects]

    def reset_window_viewport_state(self):
        self.graphic.window["x_min"] = -self.view.canvas.canvas.width()/2
        self.graphic.window["x_max"] = self.view.canvas.canvas.width()/2
        self.graphic.window["y_min"] = -self.view.canvas.canvas.height()/2
        self.graphic.window["y_max"] = self.view.canvas.canvas.height()/2

        self.graphic.viewport["x_min"] = -self.view.canvas.canvas.width()/2
        self.graphic.viewport["x_max"] = self.view.canvas.canvas.width()/2
        self.graphic.viewport["y_min"] = -self.view.canvas.canvas.height()/2
        self.graphic.viewport["y_max"] = self.view.canvas.canvas.height()/2

    def on_window_resize(self):
        self.erase()
        self.reset_window_viewport_state()
        self.draw()

    def string_to_obj(self, string_coords):
        coords = list(eval(string_coords))

        obj_type = ObjType(3)
        if(isinstance(coords[0], int) or isinstance(coords[0], float)):
            obj_type = ObjType(1)
            coords = [(coords[0], coords[1])]
        elif(len(coords)<3):
            obj_type = ObjType(2)

        return (obj_type, coords)



    def save_object(self):

        dialog = ObjectDialog()

        if dialog.exec():
            self.erase()

            (name, string_coords, color) = dialog.get_inputs()

            (obj_type, coords) = self.string_to_obj(string_coords)

            obj = GraphicObject(name, obj_type, coords, color)
            self.graphic.objects.append(obj)

            self.draw()
            self.make_list()


    def edit_object(self):
        selected = self.view.side_menu.list.currentRow()

        if(selected != -1):

            _object = self.graphic.objects[selected]
            name = _object.name
            coords = str(_object.coords)[1:-1]
            color = _object.color

            dialog = ObjectDialog(self.view, name, coords, color)
            result = dialog.exec()
            if (result):
                self.erase()
                
                (new_name, new_string_coords, new_color) = dialog.get_inputs()

                (new_obj_type, new_coords) = self.string_to_obj(new_string_coords)
                _object.name = new_name
                _object.obj_type = new_obj_type
                _object.coords = new_coords
                _object.color = new_color
            
                self.draw()
                self.make_list()

    def remove_object(self):
        selected = self.view.side_menu.list.currentRow()
        if(selected != -1):
            self.erase()

            del self.graphic.objects[selected]

            self.draw()
            self.make_list()


    def transform_object(self):

        selected = self.view.side_menu.list.currentRow()
        if(selected != -1):
            _object = self.graphic.objects[selected]
            name = _object.name
            dialog = TransformationDialog(self.view, name)
            result = dialog.exec()
            if (result):
                self.erase()

                transformation_list = [self.view_to_model_transformation(transformation) for transformation in dialog.get_transformations()]
                
                self.graphic.transform_from_list(selected, transformation_list)

                self.draw()
                self.make_list()

    def view_to_model_transformation(self, view_entry):
        transformation_type = TransformationType[view_entry[0].name]
        transformation = None
        if(transformation_type == TransformationType.ROTATION):
            transformation = (RotationType[view_entry[1][0]],view_entry[1][1],view_entry[1][2],view_entry[1][3])
        else:
            transformation = view_entry[1]

        return (transformation_type,transformation)

    def draw_color(self, color):
        obj_list = []
        for ob in self.graphic.objects:
            viewport_coords = [self.graphic.viewport_transformation(point[0],point[1]) for point in ob.coords]
            if(color == None):
                self.view.canvas.draw(viewport_coords, QColor(ob.color))
            else:
                self.view.canvas.draw(viewport_coords, color)

        self.view.canvas.update()

    def draw(self):
        self.draw_color(None)

    def erase(self):
        self.draw_color(self.bg_color)

    def make_list(self):            
        obj_list = []
        for ob in self.graphic.objects:
            obj_list.append(ob.obj_type.name + '(' + ob.name + ')')

        self.view.side_menu.make_list(obj_list)

    def reset_multiplier(self):
        if (self.view.side_menu.step.text().strip() == ""):
            self.view.side_menu.step.setText("10")

    def zoom_in(self):

        self.erase()

        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())

        zoomed = self.graphic.zoom_in(step)

        if(not zoomed):
            message_box = QMessageBox()
            message_box.setWindowTitle("Zoom in")
            message_box.setText("Too much zoom")
            message_box.setInformativeText("Set a smaller step value")
            message_box.setStandardButtons(QMessageBox.Ok)
            ret = message_box.exec()


        self.draw()

    def zoom_out(self):

        self.erase()

        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())

        self.graphic.zoom_out(step)

        self.draw()


    def pan_right(self):

        self.erase()

        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())

        self.graphic.pan_right(step)

        self.draw()


    def pan_left(self):

        self.erase()

        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())

        self.graphic.pan_left(step)

        self.draw()

    def pan_up(self):

        self.erase()

        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())

        self.graphic.pan_up(step)

        self.draw()

    def pan_down(self):

        self.erase()

        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())

        self.graphic.pan_down(step)

        self.draw()
