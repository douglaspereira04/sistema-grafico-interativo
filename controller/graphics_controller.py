from view.object_dialog import ObjectDialog
from view.transformation_dialog import TransformationDialog
from model.graphic_object import GraphicObject
from model.graphics import TransformationType, RotationType, LineClipping
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

        self.view.side_menu.rotation_slider.valueChanged.connect(self.rotate)
        self.view.side_menu.rotation_button.clicked.connect(self.rotate)


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
            self.zoom_in(self.view.canvas.wheel_y_angle*(self.graphic.window_height()/self.graphic.viewport_height())*self.graphic.zoom)
        elif(self.view.canvas.wheel_y_angle < 0):
            self.zoom_out((-1)*self.view.canvas.wheel_y_angle*(self.graphic.window_height()/self.graphic.viewport_height())*self.graphic.zoom)

    def canvas_pan(self):
        
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()    
        x_diff = x_diff*(self.graphic.window_width()/self.graphic.viewport_width())*self.graphic.zoom
        y_diff = y_diff*(self.graphic.window_height()/self.graphic.viewport_height())*self.graphic.zoom
        if(x_diff > 0):
            self.pan_left(x_diff)
        elif(x_diff < 0):
            self.pan_right(-x_diff)

        if(y_diff > 0):
            self.pan_up(y_diff)
        elif(y_diff < 0):
            self.pan_down(-y_diff)

    def object_rotate(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        selected = self.view.side_menu.list.currentRow()

        if(selected != -1):
            centroid = self.graphic.objects[selected].centroid()

            if(x_diff != 0 or y_diff != 0):
                transformation = self.graphic.natural_rotation(y_diff, centroid)
                self.transform_object([transformation])


    def object_scale(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()

        if(x_diff != 0 or y_diff != 0):
            transformation = self.graphic.scale(1-(0.01*y_diff))
            self.transform_object([transformation])

    def object_grab(self):
        (x_diff, y_diff) = self.view.canvas.get_mouse_movement()
        
        x_diff = x_diff*(self.graphic.window_width()/self.graphic.viewport_width())*self.graphic.zoom
        y_diff = y_diff*(self.graphic.window_height()/self.graphic.viewport_height())*self.graphic.zoom

        if(x_diff != 0 or y_diff != 0):
            transformation = self.graphic.translation(x_diff,-y_diff)
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
        try:
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
        except Exception as e:
            show_warning_box("Unable to save file: "+ str(e))

            

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


    def transform_object(self, transformation):

        selected = self.view.side_menu.list.currentRow()
        if(selected != -1):
            _object = self.graphic.objects[selected]
            name = _object.name

            transformation_list = []

            if(transformation == False):
                dialog = TransformationDialog(self.view, name)

                result = dialog.exec()
                if (result):
                    transformation_list = [self.view_to_model_transformation(transformation) for transformation in dialog.get_transformations()]
            else:
                transformation_list = transformation

            self.log("Trasformation: "+name+"; "+str(transformation_list))

            if(len(transformation_list) > 0):
                self.erase()

                self.graphic.transform_from_list(selected, transformation_list)

                self.draw()

    def view_to_model_transformation(self, view_entry):
        transformation_type = TransformationType[view_entry[0].name]
        transformation = None
        if(transformation_type == TransformationType.ROTATION):
            transformation = (RotationType[view_entry[1][0]],view_entry[1][1],view_entry[1][2],view_entry[1][3])
        else:
            transformation = view_entry[1]

        return (transformation_type,transformation)

    def draw_color(self, color):
        self.graphic.normalize_and_clip()

        obj_list = []
        for ob in self.graphic.display:
            viewport_coords = [self.graphic.viewport_transformation(point[0],point[1]) for point in ob[0]]
            if(color == None):
                self.view.canvas.draw(viewport_coords, QColor(ob[1]))
            else:
                self.view.canvas.draw(viewport_coords, color)

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

        zoom_by_button = step == False

        if(zoom_by_button):
            step = float(self.view.side_menu.step.text())

        zoomed = self.graphic.zoom_in(step)

        self.draw()

        if(zoom_by_button and (not zoomed)):
            show_warning_box("Too much zoom.\nSet smaller step value.")

        self.log("Zoom In: "+str(step)+"; Zoom level: "+str(self.graphic.zoom)+";")

    def zoom_out(self, step):

        self.erase()

        self.reset_multiplier()

        if(step == False):
            step = float(self.view.side_menu.step.text())

        self.graphic.zoom_out(step)

        self.draw()

        self.log("Zoom Out: "+str(step)+"; Zoom level: "+str(self.graphic.zoom)+";")


    def pan_right(self, step):

        self.erase()

        self.reset_multiplier()
        if(step == False):
            step = float(self.view.side_menu.step.text())

        self.graphic.pan_right(step)

        self.draw()

        self.log("Panning Right: "+str(step)+";")


    def pan_left(self, step):

        self.erase()

        self.reset_multiplier()
        if(step == False):
            step = float(self.view.side_menu.step.text())

        self.graphic.pan_left(step)

        self.draw()

        self.log("Panning Left: "+str(step)+";")

    def pan_up(self, step):

        self.erase()

        self.reset_multiplier()
        if(step == False):
            step = float(self.view.side_menu.step.text())

        self.graphic.pan_up(step)

        self.draw()

        self.log("Panning Up: "+str(step)+";")

    def pan_down(self, step):

        self.erase()

        self.reset_multiplier()
        if(step == False):
            step = float(self.view.side_menu.step.text())

        self.graphic.pan_down(step)

        self.draw()

        self.log("Panning Down: "+str(step)+";")

    def rotate(self, value):

        self.erase()

        self.reset_multiplier()
        step = float(self.view.side_menu.step.text())

        if(value != False):
            degrees = value*36*0.1*step
        else:
            degrees = step

        self.graphic.vup_angle = degrees

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
