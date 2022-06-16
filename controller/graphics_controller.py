from view.object_dialog import ObjectDialog
from view.transformation_dialog import TransformationDialog
from model.graphics import Axis
from model.graphic_object import GraphicObject
from model.curve_object import CurveObject
from model.point_object import PointObject
from model.line_object import LineObject
from model.wireframe_object import WireframeObject
from model.clipper import LineClipping
from model.transformation import Transformation
from model.transformation_3d import Translation3D, Scaling3D, Transformation3DType, Rotation3DType, Rotation3D, RotationAxis
from model.obj_type import ObjType
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from view.util.dialogs import show_warning_box, show_input_box
from model.wavefront_obj import WavefrontObj
import math
import os


class GraphicsController:
    def __init__(self, graphics, view):
        self.graphic = graphics
        self.view = view

        self.view.side_menu.add.connect(self.save_object)
        self.view.side_menu.edit.connect(self.edit_object)
        self.view.side_menu.remove.connect(self.remove_object)
        self.view.side_menu.transform.connect(self.transform_object)

        self.view.side_menu.rotated_right.connect(lambda : self.rotate(1))
        self.view.side_menu.rotated_left.connect(lambda : self.rotate(-1))
        self.view.side_menu.zoomed_in.connect(lambda : self.zoom_button(1))
        self.view.side_menu.zoomed_out.connect(lambda : self.zoom_button(-1))

        self.view.side_menu.up.connect(lambda : self.pan(Axis.Y,-1))
        self.view.side_menu.down.connect(lambda : self.pan(Axis.Y,1))
        self.view.side_menu.left.connect(lambda : self.pan(Axis.X, -1))
        self.view.side_menu.right.connect(lambda : self.pan(Axis.X,1))
        self.view.side_menu.forward.connect(lambda : self.pan(Axis.Z, -1))
        self.view.side_menu.backward.connect(lambda : self.pan(Axis.Z,1))


        self.view.show()

        self.reset_window_viewport_state()

        self.view.canvas.resize.connect(self.on_window_resize)

        self.bg_color = Qt.white
        self.line_color = Qt.black

        self.view.set_canvas_color(self.bg_color)

        self.view.load_from_file.triggered.connect(self.load_from_file)
        self.view.save_to_file.triggered.connect(self.save_to_file)
        self.view.enable_clipping.triggered.connect(self.config_clipping)
        self.view.lian_barsk.triggered.connect(self.config_clipping)
        self.view.cohen_sutherland.triggered.connect(self.config_clipping)

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

    def load_file(self, file_name):
        if(file_name[0]!=''):
            f = open(file_name[0], "r")
            obj_data = f.read()
            f.close()

            mtlib_map = dict()
            mtlib_name_list = WavefrontObj.get_mtlib_list(obj_data)
            for mtlib_name in mtlib_name_list:
                mtlib_path = os.path.join(os.path.dirname(file_name[0]),mtlib_name)
                f = open(mtlib_path, "r")
                mtlib_data = f.read()
                f.close()
                mtlib_map[mtlib_name] = mtlib_data
            
            (objects, window_inf) = WavefrontObj.compose(obj_data,mtlib_map)
            self.erase()

            self.graphic.objects = objects

            if(window_inf != None):
                self.graphic.set_window(window_inf)

            self.draw()
            self.make_list()

    def load_from_file(self):

        file_name = QFileDialog.getOpenFileName(self.view, 'Open file', '',"Obj files (*.obj)")
        self.load_file(file_name)
        

        self.log("Load from file: "+file_name[0]+";")



    def save_to_file(self):

        file_name = QFileDialog.getSaveFileName(self.view, 'Save file', '',"Obj files (*.obj)")
        
        file_name = file_name[0]
        
        if(file_name!=''):

            if(not file_name.endswith(".obj")):
                file_name +=".obj"

            (mtlib_name, done) = show_input_box("Mtlib name: ")

            if (done and mtlib_name!=""):

                if(not mtlib_name.endswith(".mtl")):
                    mtlib_name +=".mtl"

                (obj, mtlib) = WavefrontObj.parse(self.graphic, mtlib_name)

                mtlib_name = os.path.join(os.path.dirname(file_name),mtlib_name)

                f = open(file_name, "w")
                for line in obj:
                    f.write(line)
                f.close()


                f = open(mtlib_name, "w")
                for line in mtlib:
                    f.write(line)
                f.close()

        self.log("Save to file: "+file_name+";")


    def reset_window_viewport_state(self):

        self.graphic.viewport = {
            "x_min": (-self.view.canvas.canvas.width()/2),
            "x_max": (self.view.canvas.canvas.width()/2),
            "y_min": (-self.view.canvas.canvas.height()/2),
            "y_max": (self.view.canvas.canvas.height()/2)
        }

        self.graphic.window = {
            "width": self.view.canvas.canvas.width(),
            "height": self.view.canvas.canvas.height()
        }


    def on_window_resize(self):
        self.erase()
        window = self.graphic.get_window()
        self.reset_window_viewport_state()
        self.graphic.set_window(window)
        self.draw()

    def string_to_obj(self, string_coords):
        coords = list(eval(string_coords))

        obj_type = ObjType.WIREFRAME
        if(isinstance(coords[0], int) or isinstance(coords[0], float)):
            obj_type = ObjType.POINT
            coords = [(coords[0], coords[1], coords[2])]

        return (obj_type, coords)



    def save_object(self):

        dialog = ObjectDialog()

        if dialog.exec():

            (name, string_coords, color, filled, bezier, spline) = dialog.get_inputs()

            (obj_type, coords) = self.string_to_obj(string_coords)
            print(coords)

            if(obj_type == ObjType.POINT):
                print(coords)
                obj = PointObject(name, coords, color)
            elif(obj_type == ObjType.WIREFRAME):
                obj = WireframeObject(name, coords, color)
            
            self.erase()

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
            filled = False
            is_bezier = False
            is_spline = False

            dialog = ObjectDialog(self.view, name, coords, color, filled, is_bezier, is_spline)
            result = dialog.exec()
            if (result):
                self.erase()
                
                new_object = None
                (new_name, new_string_coords, new_color, new_filled, bezier, spline) = dialog.get_inputs()
                (new_obj_type, new_coords) = self.string_to_obj(new_string_coords)

                if(new_obj_type == ObjType.POINT):
                    new_object = PointObject(new_name, new_coords, new_color)
                else:
                    new_object = WireframeObject(new_name, new_coords, new_color)

                self.graphic.objects[selected] = new_object
            
                self.draw()
                self.make_list()

    def remove_object(self):
        selected = self.view.side_menu.list.currentRow()
        if(selected != -1):
            self.erase()

            del self.graphic.objects[selected]

            self.draw()
            self.make_list()


    def transform_object(self, transformation):

        selected = self.view.side_menu.list.currentRow()
        if(selected != -1):
            _object = self.graphic.objects[selected]
            name = _object.name

            transformation_list = []

            if(transformation == True):
                dialog = TransformationDialog(self.view, name)

                result = dialog.exec()
                if (result):
                    transformation_list = [self.view_to_model_transformation(transformation) for transformation in dialog.get_transformations()]
            else:
                transformation_list = transformation

            self.log("Trasformation: "+name+"; "+" ".join(str(t) for t in transformation_list))

            if(len(transformation_list) > 0):
                self.erase()

                self.graphic.transform_from_list(selected, transformation_list)

                self.draw()

    def view_to_model_transformation(self, view_entry):
        transformation_type = Transformation3DType[view_entry[0].name]
        transformation = None

        if(transformation_type == Transformation3DType.ROTATION):
            rotation_type = Rotation3DType[view_entry[1][0]]
            (degrees, x, y, z, axis, axis_vector) = (view_entry[1][1],view_entry[1][2],view_entry[1][3],view_entry[1][4],RotationAxis[view_entry[1][5]], view_entry[1][6])
            transformation = Rotation3D(rotation_type, axis, axis_vector, degrees, x, y, z)
        elif(transformation_type == Transformation3DType.TRANSLATION):
            (x, y, z) = view_entry[1]
            transformation = Translation3D(x, y, z)
        elif(transformation_type == Transformation3DType.SCALING):
            factor = view_entry[1]
            transformation = Scaling3D(factor)

        return transformation

    def draw_color(self, color):
        self.graphic.normalize_and_clip()

        obj_list = []
        for display_object in self.graphic.display:
            if(color == None):
                obj_color = QColor(display_object.color)
            else:
                obj_color = color

            if((not display_object.is_filled) and (len(display_object.coords) > 1)):
                for i in range(0, len(display_object.coords)-1, 2):
                    p0 = display_object.coords[i]
                    p1 = display_object.coords[i+1]
                    self.view.canvas.draw([p0,p1], obj_color, False)
            else:
                self.view.canvas.draw(display_object.coords, obj_color, display_object.is_filled)

        self.view.canvas.update()

    def draw(self):
        self.draw_color(None)
        color = QColor("#FFCFCF")
        self.draw_viewport_limits(color)


    def erase(self):
        self.draw_color(self.bg_color)
        self.draw_viewport_limits(self.bg_color)

    def draw_viewport_limits(self, color):
        width = self.graphic.viewport_width()
        height = self.graphic.viewport_height()

        border = self.graphic.border
        
        coords = [(border,border), (border,height-border), (width-border, height-border), (width-border, border), (border,border)]
        self.view.canvas.draw(coords, color)


    def make_list(self):            
        obj_list = []
        for ob in self.graphic.objects:
            obj_list.append(ob.obj_type.name + '(' + ob.name + ')')

        self.view.side_menu.make_list(obj_list)

    def reset_multiplier(self):
        if (self.view.side_menu.step.text().strip() == ""):
            self.view.side_menu.step.setText("10")

    def zoom_button(self, direction):
        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())
        self.zoom(step*direction)

    def zoom(self, step):
        self.erase()
        self.graphic.zoom(step)
        self.draw()
        self.log("Zoom: "+str(step)+";")



    def pan(self, axis, direction):
        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())

        self.erase()
        
        self.graphic.pan(axis, step*direction)

        self.draw()
        self.log("Panning: ("+str(axis.name)+" axis, "+str(step*direction)+");")

    def rotate(self, direction):


        self.erase()
        self.reset_multiplier()
        degrees = float(self.view.side_menu.step.text())


        if(self.view.side_menu.x_axis_check.isChecked()):
            axis = Axis.X
        elif(self.view.side_menu.y_axis_check.isChecked()):
            axis = Axis.Y
        else:
            axis = Axis.Z

        self.graphic.rotate(axis, degrees*direction)

        self.draw()
        self.log("Rotate: ("+str(axis.name)+" axis, "+str(degrees*direction)+");")


    def log(self,text):
        self.view.log.appendPlainText(text)

    def config_clipping(self):
        self.erase()
        
        if(self.view.enable_clipping.isChecked()):
            self.graphic.enable_clipping = True
        else:
            self.graphic.enable_clipping = False

        if(self.view.lian_barsk.isChecked()):
            self.graphic.line_clipping = LineClipping.LIAN_BARSK
        else:
            self.graphic.line_clipping = LineClipping.COHEN_SUTHERLAND

        self.draw()
