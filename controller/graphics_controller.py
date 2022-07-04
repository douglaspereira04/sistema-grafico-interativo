from view.object_dialog import ObjectDialog
from view.transformation_dialog import TransformationDialog
from model.graphics import Axis
from model.graphic_element import GraphicElement
from model.graphic_object import GraphicObject
from model.curve_object import CurveObject
from model.point_3d import Point3D
from model.line_object import LineObject
from model.wireframe_3d import Wireframe3D
from model.bicubic_surface import BicubicSurface
from model.clipper import LineClipping
from model.transformation import Transformation
from model.transformation_3d import Translation3D, Scaling3D, Transformation3DType, Rotation3DType, Rotation3D, RotationAxis, Transformation3D
from model.obj_type import ObjType
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from view.util.dialogs import show_warning_box, show_input_box
from model.wavefront_obj import WavefrontObj
import math
import os
import numpy as np


class GraphicsController:
    def __init__(self, graphics, view):
        self.graphic = graphics
        self.view = view

        self.view.side_menu.add.connect(self.save_object)
        self.view.side_menu.edit.connect(self.edit_object)
        self.view.side_menu.remove.connect(self.remove_object)
        self.view.side_menu.transform.connect(self.transform_object)

        self.view.side_menu.rotated_right.connect(lambda : self.rotate_button(1))
        self.view.side_menu.rotated_left.connect(lambda : self.rotate_button(-1))
        self.view.side_menu.zoomed_in.connect(lambda : self.zoom_button(1))
        self.view.side_menu.zoomed_out.connect(lambda : self.zoom_button(-1))

        self.view.side_menu.up.connect(lambda : self.pan(Axis.Y,1))
        self.view.side_menu.down.connect(lambda : self.pan(Axis.Y,-1))
        self.view.side_menu.left.connect(lambda : self.pan(Axis.X, 1))
        self.view.side_menu.right.connect(lambda : self.pan(Axis.X,-1))
        self.view.side_menu.forward.connect(lambda : self.pan(Axis.Z, 1))
        self.view.side_menu.backward.connect(lambda : self.pan(Axis.Z,-1))


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



        self.view.canvas.zoom.connect(self.canvas_scroll)
        self.view.canvas.pan.connect(self.canvas_pan)
        self.view.canvas.rotate_xy_window.connect(self.canvas_rotate_xy)
        self.view.canvas.rotate_z_window.connect(self.canvas_rotate_z)
        self.view.canvas.rotate.connect(self.object_rotate)
        self.view.canvas.scale.connect(self.object_scale)
        self.view.canvas.grab.connect(self.object_grab)





    def canvas_scroll(self):
        if(self.view.canvas.wheel_y_angle != 0):
            step = self.view.canvas.wheel_y_angle*(self.graphic.window_height()/self.graphic.viewport_height());
            self.zoom(step)

    def canvas_pan(self):
        
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()    
        x_diff = x_diff*(self.graphic.window_width()/self.graphic.viewport_width())/10
        y_diff = y_diff*(self.graphic.window_height()/self.graphic.viewport_height())/10
        if(x_diff != 0):
            self.pan(Axis.X,x_diff)

        if(y_diff != 0):
            self.pan(Axis.Y,y_diff)


    def canvas_rotate_xy(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()
        if(x_diff != 0):
            self.rotate(x_diff,Axis.Y,-1)
        if(y_diff != 0):
            self.rotate(y_diff,Axis.X,1)

    def canvas_rotate_z(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        if(y_diff != 0 or x_diff != 0):
            self.rotate(y_diff+x_diff,Axis.Z,1)



    def object_rotate(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        selected = self.view.side_menu.list.currentRow()
        if(selected != -1 and y_diff != 0):
            transformation = Rotation3D(Rotation3DType.OBJECT_CENTER, RotationAxis.U, self.graphic.vpn.coords[:3], y_diff, 0, 0, 0)
            transformation_list = list()
            transformation_list.append(transformation)
            self.transform_object(transformation_list)

    def object_grab(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        x_diff = x_diff*self.graphic.window_width()/self.graphic.viewport_width()
        y_diff = y_diff*self.graphic.window_height()/self.graphic.viewport_height()

        selected = self.view.side_menu.list.currentRow()
        if(selected != -1 and (x_diff != 0 or y_diff != 0)):

            translation_vector = (x_diff, -y_diff, 0)

            (x,y,z,_) = self.graphic.vrp.coords
            translation_matrix = Transformation3D.translation_matrix(-x,-y,-z)

            (x_angle, y_angle, z_angle) = self.graphic.get_angles()
            rotation_x = Transformation3D.rotation_x_matrix(x_angle)
            rotation_y = Transformation3D.rotation_y_matrix(y_angle)
            rotation_z = Transformation3D.rotation_z_matrix(z_angle)

            rotation_matrix = rotation_x @ rotation_y @ rotation_z

            t_projection_matrix = np.transpose(translation_matrix @ rotation_matrix)

            translation_vector = Translation3D.transform_3d_point(translation_vector,t_projection_matrix)
            (x,y,z) = translation_vector

            transformation = Translation3D(x,y,z)
            transformation_list = list()
            transformation_list.append(transformation)
            self.transform_object(transformation_list)


    def object_scale(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        selected = self.view.side_menu.list.currentRow()
        if(selected != -1 and y_diff != 0):
            transformation = Scaling3D(1-(0.01*y_diff))
            transformation_list = list()
            transformation_list.append(transformation)
            self.transform_object(transformation_list)



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
            "height": self.view.canvas.canvas.height(),
            "depth": self.graphic.window["depth"]
        }


    def on_window_resize(self):
        self.erase()
        window = self.graphic.get_window()
        self.reset_window_viewport_state()
        self.graphic.set_window(window)
        self.draw()


    def get_element(self, name, _list, _type, color, filled):

        if(len(_list) == 1):
            return Point3D(coords=_list[0], color=color)

        elif(_type == "Line/Wireframe" or _type == "Object (Points/Lines/Wireframes)"):
            vertices = list()
            for point in _list:
                vertex = np.array([point[0],point[1],point[2],1])
                vertices.append(vertex)

            return Wireframe3D(vertices=vertices, color=color, filled=filled)
        elif(_type == "Spline" or _type == "Bezier"):
            control_points = list()
            for point in _list:
                control_points.append(np.array([point[0],point[1],point[2],1]))

            curve_type = None
            if(_type == "Spline"):
                curve_type = ObjType.SPLINE
            elif(_type == "Bezier"):
                curve_type = ObjType.BEZIER
            return CurveObject(obj_type=curve_type, coords=control_points, color=color, filled=filled)
        else:
            return None


    def get_object(self, name, _object, color, filled, _type):
        element_list = list()
        
        if(_type == "Bezier Surface"):
            shape = np.shape(_object)
            coords = np.reshape(_object,((shape[0]*shape[1]), shape[2]))

            points = [np.array([p[0],p[1],p[2],1]) for p in coords]

            element = BicubicSurface(obj_type=ObjType.BEZIER_SURFACE, coords=points, shape=shape, color=color, filled=filled)
            element_list.append(element)
            
        else:
            for point_list in _object:
                element = self.get_element(name, point_list, _type, color, filled)
                element_list.append(element)

        return GraphicObject(name, element_list)

    def save_object(self):

        dialog = ObjectDialog()

        if dialog.exec():
            obj = None
            (name, _object, color, filled, _type) = dialog.get_inputs()

            obj = self.get_object(name, _object, color, filled, _type)

            self.erase()

            self.graphic.objects.append(obj)

            self.draw()
            self.make_list()


    def edit_object(self):
        selected = self.view.side_menu.list.currentRow()

        if(selected != -1):

            _object = self.graphic.objects[selected]
            name = _object.name
            coords = ""
            for element in _object.elements:
                coords += str(element) +";"
            coords = coords[:-1]
            color = _object.elements[0].color
            filled = _object.elements[0].filled

            _type = None
            if(len(_object.elements) == 1):
                if(_object.elements[0].obj_type == ObjType.POINT):
                    _type = "Point"
                elif(_object.elements[0].obj_type == ObjType.WIREFRAME):
                    _type = "Line/Wireframe"
                elif(_object.elements[0].obj_type == ObjType.BEZIER_SURFACE):
                    _type = "Bezier Surface"
                elif(_object.elements[0].obj_type == ObjType.BEZIER):
                    _type = "Bezier"
                elif(_object.elements[0].obj_type == ObjType.SPLINE):
                    _type = "Spline"
            else:
                _type = "Object (Points/Lines/Wireframes)"

            dialog = ObjectDialog(self.view, name, coords, color, filled, _type)
            result = dialog.exec()
            if (result):
                obj = None
                (name, _object, color, filled, _type) = dialog.get_inputs()

                obj = self.get_object(name, _object, color, filled, _type)

                self.erase()

                self.graphic.objects[selected] = obj
            
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
        self.graphic.normalize_and_clip(self.view.canvas.get_painter(), color)

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
            if(len(ob.elements) == 1):
                obj_list.append(ob.elements[0].obj_type.name + '(' + ob.name + ')')
            else:
                obj_list.append('OBJECT (' + ob.name + ')')


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


    def rotate(self, step, axis, direction):


        self.erase()
        degrees = step

        self.graphic.rotate(axis, math.radians(degrees)*direction)

        self.draw()
        self.log("Rotate: ("+str(axis.name)+" axis, "+str(degrees*direction)+");")


    def rotate_button(self, direction):

        if(self.view.side_menu.x_axis_check.isChecked()):
            axis = Axis.X
        elif(self.view.side_menu.y_axis_check.isChecked()):
            axis = Axis.Y
        else:
            axis = Axis.Z

        degrees = float(self.view.side_menu.step.text())
        self.rotate(degrees, axis, direction)


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
