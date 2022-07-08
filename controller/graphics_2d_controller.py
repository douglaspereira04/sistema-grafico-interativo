from view.object_2d_dialog import Object2DDialog
from view.transformation_dialog import TransformationDialog
from model.graphics_2d.graphics_2d import Axis
from model.graphics_2d.graphic_2d_element import Graphic2DElement
from model.graphics_2d.graphic_2d_object import Graphic2DObject
from model.graphics_2d.curve_2d import Curve2D
from model.graphics_2d.point_2d import Point2D
from model.graphics_2d.wireframe_2d import Wireframe2D
from model.clipper import LineClipping
from model.graphics_2d.transformation_2d import Translation2D, Scaling2D, Transformation2DType, Rotation2DType, Rotation2D, Transformation2D
from model.obj_type import ObjType
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from view.util.dialogs import show_warning_box, show_input_box
from model.wavefront_obj import WavefrontObj
import math
import os
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import QPoint


class Graphics2DController:
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

        self.view.side_menu.up.connect(lambda : self.pan_button(Axis.Y,1))
        self.view.side_menu.down.connect(lambda : self.pan_button(Axis.Y,-1))
        self.view.side_menu.left.connect(lambda : self.pan_button(Axis.X, 1))
        self.view.side_menu.right.connect(lambda : self.pan_button(Axis.X,-1))


        self.view.show()

        self.reset_window_viewport_state()

        self.view.canvas.resize.connect(self.on_window_resize)

        self.bg_color = Qt.white
        self.line_color = Qt.black

        self.view.set_canvas_color(self.bg_color)

        self.view.load_from_file.triggered.connect(self.load_from_file)
        self.view.save_to_file.triggered.connect(self.save_to_file)
        self.view.import_as_object.triggered.connect(self.import_as_object)
        self.view.enable_clipping.triggered.connect(self.config_clipping)
        self.view.lian_barsk.triggered.connect(self.config_clipping)
        self.view.cohen_sutherland.triggered.connect(self.config_clipping)

        self.view.side_menu.list.currentRowChanged.connect(self.list_selected)
        self.set_enable_object_options(False)



        self.view.canvas.zoom.connect(self.canvas_scroll)
        self.view.canvas.pan.connect(self.canvas_pan)
        self.view.canvas.rotate_z_window.connect(self.canvas_rotate)
        self.view.canvas.rotate.connect(self.object_rotate)
        self.view.canvas.scale.connect(self.object_scale)
        self.view.canvas.grab.connect(self.object_grab)

        self.view.projection_menu.setEnabled(False)
        self.view.side_menu.forward_label.setVisible(False)
        self.view.side_menu.backward_label.setVisible(False)
        self.view.side_menu.x_axis_label.setVisible(False)
        self.view.side_menu.x_axis_check.setVisible(False)
        self.view.side_menu.y_axis_label.setVisible(False)
        self.view.side_menu.y_axis_check.setVisible(False)
        self.view.side_menu.z_axis_label.setVisible(False)
        self.view.side_menu.z_axis_check.setVisible(False)
        for i in range (5,10):
            self.view.canvas_control_layout.itemAt(i).widget().setVisible(False)
        self.view.canvas_control_layout.itemAt(10).widget().setEnabled(False)


    def canvas_scroll(self):
        if(self.view.canvas.wheel_y_angle != 0):
            step = self.view.canvas.wheel_y_angle*(self.graphic.window_height()/self.graphic.viewport_height());
            self.zoom(step)

    def canvas_pan(self):
        
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()    
        x_diff = x_diff*(self.graphic.window_width()/self.graphic.viewport_width())
        y_diff = y_diff*(self.graphic.window_height()/self.graphic.viewport_height())
        if(x_diff != 0):
            self.pan(Axis.X,x_diff,-1)

        if(y_diff != 0):
            self.pan(Axis.Y,y_diff,1)

    def canvas_rotate(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        if(y_diff != 0 or x_diff != 0):
            self.rotate(y_diff+x_diff,1)


    def object_rotate(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        transformation_list = list()
        selected = self.view.side_menu.list.currentRow()
        if(selected != -1):
            if(y_diff != 0 or x_diff != 0):
                transformation = Rotation2D(Rotation2DType.OBJECT_CENTER, x_diff+y_diff, 0, 0)
                transformation_list.append(transformation)
        
        self.transform_object(transformation_list)

    def object_grab(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        x_diff = x_diff*self.graphic.window_width()/self.graphic.viewport_width()
        y_diff = y_diff*self.graphic.window_height()/self.graphic.viewport_height()

        selected = self.view.side_menu.list.currentRow()
        if(selected != -1 and (x_diff != 0 or y_diff != 0)):

            translation_vector = np.array([x_diff, -y_diff, 1.])

            vup_angle = self.graphic.get_vup_angle()
            rotation_matrix = Transformation2D.rotation_matrix(-vup_angle)

            translation_vector = Transformation2D.transform_point(translation_vector,rotation_matrix)
            (x,y,_) = translation_vector

            transformation = Translation2D(x,y)
            transformation_list = list()
            transformation_list.append(transformation)
            self.transform_object(transformation_list)


    def object_scale(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        selected = self.view.side_menu.list.currentRow()
        if(selected != -1 and y_diff != 0):
            transformation = Scaling2D(1-(0.01*y_diff))
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
            
            return WavefrontObj.compose(obj_data,mtlib_map)
        return None

    def load_from_file(self):

        file_name = QFileDialog.getOpenFileName(self.view, 'Open file', '',"Obj files (*.obj)")
        obj_data = self.load_file(file_name)
        if(not(obj_data is None)):
            (objects, window_inf) = obj_data
            self.erase()

            self.graphic.objects = objects

            if(window_inf != None):
                self.graphic.set_window(window_inf)

            self.draw()
            self.make_list()

            self.update_graphics_info()
            self.log("Load from file: "+file_name[0]+";")

    def import_as_object(self):

        file_name = QFileDialog.getOpenFileName(self.view, 'Open file', '',"Obj files (*.obj)")
        obj_data = self.load_file(file_name)
        
        if(not(obj_data is None)):

            (objects, window_inf) = obj_data
            name = os.path.splitext(os.path.basename(file_name[0]))[0]
            single_object = Graphic2DObject(name = name)
            for obj in objects:
                single_object.elements += obj.elements

            self.erase()

            self.graphic.objects.append(single_object)

            self.draw()
            self.make_list()

            self.log("Import from file: "+file_name[0]+";")




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
        self.update_graphics_info()


    def get_element(self, name, _list, _type, color, filled):

        if(len(_list) == 1):
            return Point2D(coords=_list[0], color=color)

        elif(_type == "Line/Wireframe" or _type == "Object (Points/Lines/Wireframes)"):
            vertices = list()
            for p in _list:
                vertex = np.array([float(p[0]),float(p[1]),1.0])
                vertices.append(vertex)

            return Wireframe2D(vertices=vertices, color=color, filled=filled)
        elif(_type == "Spline" or _type == "Bezier"):
            control_points = list()
            for p in _list:
                control_points.append(np.array([float(p[0]),float(p[1]),1.0]))

            curve_type = None
            if(_type == "Spline"):
                curve_type = ObjType.SPLINE
            elif(_type == "Bezier"):
                curve_type = ObjType.BEZIER
            return Curve2D(obj_type=curve_type, coords=control_points, color=color, filled=filled)
        else:
            return None


    def get_object(self, name, _object, color, filled, _type):
        element_list = list()
        
        for point_list in _object:
            element = self.get_element(name, point_list, _type, color, filled)
            element_list.append(element)

        return Graphic2DObject(name, element_list)

    def save_object(self):

        dialog = Object2DDialog()

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
                elif(_object.elements[0].obj_type == ObjType.BEZIER):
                    _type = "Bezier"
                elif(_object.elements[0].obj_type == ObjType.SPLINE):
                    _type = "Spline"
            else:
                _type = "Object (Points/Lines/Wireframes)"

            dialog = Object2DDialog(self.view, name, coords, color, filled, _type)
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
        transformation_type = Transformation2DType[view_entry[0].name]
        transformation = None

        if(transformation_type == Transformation2DType.ROTATION):
            rotation_type = Rotation2DType[view_entry[1][0]]
            (degrees, x, y, z, axis, axis_vector) = (view_entry[1][1],view_entry[1][2],view_entry[1][3],view_entry[1][4],RotationAxis[view_entry[1][5]], view_entry[1][6])
            transformation = Rotation2D(rotation_type, degrees, x, y)
        elif(transformation_type == Transformation2DType.TRANSLATION):
            (x, y, z) = view_entry[1]
            transformation = Translation2D(x, y)
        elif(transformation_type == Transformation2DType.SCALING):
            factor = view_entry[1]
            transformation = Scaling2D(factor)

        return transformation



    """
    Desenha os objetos dado um painter.
    """
    def draw_objects(self, color, painter):
        objects = self.graphic.objects
        line_clipping = self.graphic.line_clipping

        display = list()
        if(not (color is None)):
            painter.setPen(color)
            painter.setBrush(QtGui.QBrush(color))
            for obj in objects:
                for element in obj.elements:
                    self.draw_element(element, color, painter)

        else:
            normalization_matrix = self.graphic.normalization_matrix()
            viewport_transformation_matrix = self.graphic.viewport_transformation_matrix()
            d = 1/10
            
            for obj in objects:
                for element in obj.elements:
                    element.normalize(None, normalization_matrix, line_clipping, d,viewport_transformation_matrix)
                    color = QtGui.QColor(element.color)
                    self.draw_element(element, color, painter)

        self.view.canvas.update()

    """
    Desenha com painter um dado elemento gráfico, com a cor color
    """
    def draw_element(self,element, color, painter):
        viewported = element.viewported
        painter.setPen(color)
        painter.setBrush(QtGui.QBrush(color))

        if(element.obj_type == ObjType.POINT):
            if(not (viewported is None)):
                painter.drawPoint(viewported[0][0], viewported[0][1])

        elif((element.obj_type == ObjType.WIREFRAME or element.obj_type == ObjType.BEZIER or element.obj_type == ObjType.SPLINE) and (not element.filled)):
            if(len(viewported) > 0):
                for line in element.viewported:
                    painter.drawLine(line[0][0],line[0][1],line[1][0],line[1][1])

        elif((element.obj_type == ObjType.BEZIER or element.obj_type == ObjType.SPLINE or element.obj_type == ObjType.WIREFRAME) and element.filled):
            if(not (viewported is None)):
                vertices = [QPoint(p[0], p[1]) for p in element.viewported]
                polygon = QtGui.QPolygon(vertices)
                painter.drawPolygon(polygon)

    def draw(self,color = None):
        painter = self.view.canvas.get_painter()
        self.draw_objects(color, painter)

        painter.end()
        if(color is None):
            color = QColor("#FFCFCF")
        self.draw_viewport_limits(color)


    def erase(self):
        self.draw(self.bg_color)

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
                _type = None

                if(ob.elements[0].obj_type == ObjType.WIREFRAME and len(ob.elements[0].vertices) == 2):
                    _type = ObjType.LINE
                else:
                    _type = ob.elements[0].obj_type

                obj_list.append(_type.name + '(' + ob.name + ')')
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

        self.update_graphics_info()
        self.log("Zoom: "+str(step)+";")


    def pan_button(self, axis, direction):
        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())
        self.pan(axis, direction, step)

    def pan(self, axis, direction, step):
        self.erase()
        
        self.graphic.pan(axis, step*direction)

        self.draw()

        self.update_graphics_info()
        self.log("Panning: ("+str(axis.name)+" axis, "+str(step*direction)+");")


    def rotate(self, step, direction):


        self.erase()
        degrees = step

        self.graphic.rotate(math.radians(degrees)*direction)

        self.draw()

        self.update_graphics_info()
        self.log("Rotate: "+str(degrees*direction)+";")


    def rotate_button(self, direction):
        self.reset_multiplier()

        degrees = float(self.view.side_menu.step.text())
        self.rotate(degrees, direction)


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

    def update_graphics_info(self):
        v_w = self.graphic.viewport_width()
        v_h = self.graphic.viewport_height()
        w_w = self.graphic.window_width()
        w_h = self.graphic.window_height()

        self.view.viewport_info.setText(str(round(v_w,2))+" x "+ str(round(v_h,2)))
        self.view.window_info.setText(str(round(w_w,2))+" x "+ str(round(w_h,2)))