from view.object_dialog import ObjectDialog
from view.transformation_dialog import TransformationDialog
from model.graphic_object import GraphicObject
from model.curve_object import CurveObject
from model.point_object import PointObject
from model.line_object import LineObject
from model.wireframe_object import WireframeObject
from model.clipper import LineClipping
from model.transformation import TransformationType, RotationType, Rotation, Translation, Scaling, Transformation
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
        self.view.side_menu.zoomed_in.connect(self.zoom_in)
        self.view.side_menu.zoomed_out.connect(self.zoom_out)

        self.view.side_menu.up.connect(lambda : self.pan_button(0,-1))
        self.view.side_menu.down.connect(lambda : self.pan_button(0,1))
        self.view.side_menu.left.connect(lambda : self.pan_button(-1,0))
        self.view.side_menu.right.connect(lambda : self.pan_button(1,0))


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

        self.view.test_normalization.triggered.connect(self.toggle_normalization_test)
        self.normalization_test = None

        self.view.side_menu.list.currentRowChanged.connect(self.list_selected)
        self.set_enable_object_options(False)

        self.view.canvas.zoom.connect(self.canvas_scroll)
        self.view.canvas.pan.connect(self.canvas_pan)
        self.view.canvas.rotate.connect(self.object_rotate)
        self.view.canvas.scale.connect(self.object_scale)
        self.view.canvas.grab.connect(self.object_grab)


    def canvas_scroll(self):
        if(self.view.canvas.wheel_y_angle > 0):
            self.zoom_in(self.view.canvas.wheel_y_angle*(self.graphic.window_height()/self.graphic.viewport_height()))
        elif(self.view.canvas.wheel_y_angle < 0):
            self.zoom_out((-1)*self.view.canvas.wheel_y_angle*(self.graphic.window_height()/self.graphic.viewport_height()))


    def canvas_pan(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()    
        x_diff = x_diff*(self.graphic.window_width()/self.graphic.viewport_width())
        y_diff = y_diff*(self.graphic.window_height()/self.graphic.viewport_height())

        if(x_diff != 0 or y_diff != 0):
            self.pan(-x_diff, -y_diff)


    def object_rotate(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        selected = self.view.side_menu.list.currentRow()

        if(selected != -1):
            if(x_diff != 0 or y_diff != 0):
                transformation = Rotation(RotationType.OBJECT_CENTER, y_diff, 0, 0)
                self.transform_object([transformation])


    def object_scale(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        if(x_diff != 0 or y_diff != 0):
            transformation = Scaling(1-(0.01*y_diff))
            self.transform_object([transformation])

    def object_grab(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()
        
        x_diff = x_diff*(self.graphic.window_width()/self.graphic.viewport_width())
        y_diff = y_diff*(self.graphic.window_height()/self.graphic.viewport_height())

        if(x_diff != 0 or y_diff != 0):
            (x_diff, y_diff) = self.graphic.rotate_view_vector(x_diff,y_diff)
            transformation = Translation(x_diff,-y_diff)
            self.transform_object([transformation])


    def list_selected(self):
        if(self.view.side_menu.list.currentRow() >= 0):
            self.set_enable_object_options(True)
        else:
            self.set_enable_object_options(False)

    def set_enable_object_options(self, enabled):
        self.view.side_menu.transform_btn.setEnabled(enabled)
        self.view.side_menu.remove_btn.setEnabled(enabled)


    def load_from_file(self):

        file_name = QFileDialog.getOpenFileName(self.view, 'Open file', '',"Obj files (*.obj)")

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
            "x_min": (-self.view.canvas.canvas.width()/2),
            "x_max": (self.view.canvas.canvas.width()/2),
            "y_min": (-self.view.canvas.canvas.height()/2),
            "y_max": (self.view.canvas.canvas.height()/2)
        }


    def on_window_resize(self):
        self.erase()
        window = self.graphic.get_window()
        self.reset_window_viewport_state()
        self.graphic.set_window(window)
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

            (name, string_coords, color, filled, bezier, spline) = dialog.get_inputs()

            (obj_type, coords) = self.string_to_obj(string_coords)

            if(bezier):
                obj = CurveObject(name, ObjType.BEZIER, coords, color, filled)
            elif(spline):
                obj = CurveObject(name, ObjType.SPLINE, coords, color, filled)
            elif(obj_type == ObjType.POINT):
                obj = PointObject(name, coords, color)
            elif(obj_type == ObjType.LINE or obj_type == ObjType.WIREFRAME):
                obj = WireframeObject(name, coords, color, filled)
            
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
            filled = _object.filled
            is_bezier = _object.obj_type == ObjType.BEZIER
            is_spline = _object.obj_type == ObjType.SPLINE

            dialog = ObjectDialog(self.view, name, coords, color, filled, is_bezier, is_spline)
            result = dialog.exec()
            if (result):
                self.erase()
                
                new_object = None
                (new_name, new_string_coords, new_color, new_filled, bezier, spline) = dialog.get_inputs()
                (new_obj_type, new_coords) = self.string_to_obj(new_string_coords)

                if(bezier):
                    new_object = CurveObject(new_name, ObjType.BEZIER, new_coords, new_color, new_filled)
                elif(spline):
                    new_object = CurveObject(new_name, ObjType.SPLINE, new_coords, new_color, new_filled)
                elif(new_obj_type == ObjType.POINT):
                    new_object = PointObject(new_name, new_coords, new_color)
                elif(new_obj_type == ObjType.LINE):
                    new_object = LineObject(new_name, new_coords, new_color)
                else:
                    new_object = WireframeObject(new_name, new_coords, new_color, new_filled)

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
        transformation_type = TransformationType[view_entry[0].name]
        transformation = None

        if(transformation_type == TransformationType.ROTATION):
            (rotation_type, degrees, x, y) = (RotationType[view_entry[1][0]], view_entry[1][1],view_entry[1][2],view_entry[1][3])
            transformation = Rotation(rotation_type, degrees, x, y)
        elif(transformation_type == TransformationType.TRANSLATION):
            (x, y) = view_entry[1]
            transformation = Translation(x, y)
        elif(transformation_type == TransformationType.SCALING):
            factor = view_entry[1]
            transformation = Scaling(factor)

        return transformation

    def draw_color(self, color):
        self.graphic.normalize_and_clip()

        obj_list = []
        for display_object in self.graphic.display:
            if(color == None):
                obj_color = QColor(display_object.color)
            else:
                obj_color = color

            if((self.graphic.enable_clipping) and (not display_object.is_filled) and (len(display_object.coords) > 1)):
                for i in range(0, len(display_object.coords)-1, 2):
                    p0 = display_object.coords[i]
                    p1 = display_object.coords[i+1]
                    self.view.canvas.draw([p0,p1], obj_color, False)
            else:
                self.view.canvas.draw(display_object.coords, obj_color, display_object.is_filled)

        self.view.canvas.update()

    def draw(self):
        self.draw_color(None)

        if(self.normalization_test != None):
            try:
                print(self.graphic.display[len(self.graphic.display)-1][0])
            except:
                print(None)

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

    def zoom_in(self, step):

        self.erase()

        self.reset_multiplier()

        zoom_by_button = step == True

        if(zoom_by_button):
            step = float(self.view.side_menu.step.text())

        zoomed = self.graphic.zoom_in(step)

        self.draw()

        if(zoom_by_button and (not zoomed)):
            show_warning_box("Too much zoom.\nSet smaller step value.")

        self.log("Zoom In: "+str(step)+";")

    def zoom_out(self, step):

        self.erase()

        self.reset_multiplier()

        zoom_by_button = step == True

        if(zoom_by_button):
            step = float(self.view.side_menu.step.text())

        self.graphic.zoom_out(step)

        self.draw()

        self.log("Zoom Out: "+str(step)+";")


    def pan_button(self, x, y):
        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())

        self.pan(x*step, y*step)


    def pan(self, x, y):

        self.erase()

        self.graphic.pan(x, y)

        self.draw()

        self.log("Panning: ("+str(x)+","+str(y)+");")

    def rotate(self, direction):
        self.erase()

        self.reset_multiplier()
        degrees = float(self.view.side_menu.step.text())

        self.graphic.vup_angle += degrees*direction

        self.draw()
        self.log("Rotate: "+str(degrees)+"°;")


    def log(self,text):
        self.view.log.appendPlainText(text)


    def toggle_normalization_test(self):
        if (self.normalization_test != None):
            self.erase()
            del self.graphic.objects[self.normalization_test]
            self.normalization_test = None

        else:
            (x,y) = self.graphic.window_center()
            (name, string_coords, color) = ("Normalization_Test","("+str(x)+","+str(y)+")","#FF0000")

            (obj_type, coords) = self.string_to_obj(string_coords)

            obj = GraphicObject(name, obj_type, coords, color)


            self.erase()
            self.graphic.objects.append(obj)

            self.normalization_test = len(self.graphic.objects) -1

        self.draw()
        self.make_list()

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
