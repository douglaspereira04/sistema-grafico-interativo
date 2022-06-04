from view.object_3d_dialog import Object3dDialog
from view.transformation_3d_dialog import Transformation3dDialog
from model.graphics import TransformationType, RotationType, LineClipping
from model.graphic_3d_object import Axis
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from view.util.dialogs import show_warning_box, show_input_box
from model.wavefront_obj import WavefrontObj
import math
import os


class Graphics3dController:
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


    def save_object(self):

        dialog = Object3dDialog(self.view)
        obj = None
        err = None
        if dialog.exec():
            try:
                obj = dialog.get_obj()
                if(obj != None):
                    #self.erase()

                    self.graphic.objects.append(obj)

                    #self.draw()
                    self.make_list()
            except Exception as e:
                err = e

            if(obj == None):
                show_warning_box("Unable to create object: "+str(err))

    def edit_object(self):
        selected = self.view.side_menu.list.currentRow()
        if(selected != -1):

            _object = self.graphic.objects[selected]
            name = _object.name
            vertices = str([(vertice.x,vertice.y,vertice.z) for vertice in _object.vertices])
            edges = str(_object.edges)
            color = _object.color

            err = None
            new_obj = None
            dialog = Object3dDialog(self.view, name, vertices, edges, color)
            if(dialog.exec()):
                try:
                    new_obj = dialog.get_obj()
                    if(new_obj != None):
                        #self.erase()

                        _object.name = new_obj.name
                        _object.vertices = new_obj.vertices
                        _object.edges = new_obj.edges
                        _object.color = new_obj.color

                        #self.draw()
                        self.make_list()
                except Exception as e:
                    err = e

                if(new_obj == None):
                    show_warning_box("Unable to create object: "+str(err))

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
                dialog = Transformation3dDialog(self.view, name)

                result = dialog.exec()
                if (result):
                    transformation_list = [self.view_to_model_transformation(transformation) for transformation in dialog.get_transformations()]
            else:
                transformation_list = transformation

            self.log("Trasformation: "+name+"; "+str(transformation_list))

            if(len(transformation_list) > 0):
                #self.erase()

                self.graphic.transform_from_list(selected, transformation_list)

                #self.draw()

    def view_to_model_transformation(self, view_entry):
        transformation_type = TransformationType[view_entry[0].name]
        transformation = None
        if(transformation_type == TransformationType.ROTATION):
            transformation = (RotationType[view_entry[1][0]],view_entry[1][1],view_entry[1][2],view_entry[1][3],view_entry[1][4],Axis[view_entry[1][5]])
        else:
            transformation = view_entry[1]

        return (transformation_type,transformation)

    def draw_color(self, color):
        self.graphic.normalize_and_clip()

        obj_list = []
        for ob in self.graphic.display:
            viewport_coords = [self.graphic.viewport_transformation(point[0],point[1]) for point in ob[0]]
            if(color == None):
                filled = False
                if(len(ob[0])>2):
                    filled = ob[2]
                self.view.canvas.draw(viewport_coords, QColor(ob[1]), filled)
            else:
                filled = False
                if(len(ob[0])>2):
                    filled = ob[2]
                self.view.canvas.draw(viewport_coords, color, filled)

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
            obj_list.append('(' + ob.name + ')')

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
