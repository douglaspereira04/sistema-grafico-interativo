from view.object_dialog import ObjectDialog
from model.graphic_object import GraphicObject
from model.obj_type import ObjType


class GraphicsController:
    def __init__(self, graphics, view):
        self.graphic = graphics
        self.view = view

        self.view.side_menu.zin_btn.clicked.connect(lambda: self.zoom_in())
        self.view.side_menu.zout_btn.clicked.connect(lambda: self.zoom_out())
        self.view.side_menu.add_btn.clicked.connect(lambda: self.save_object())

        self.view.side_menu.left_btn.clicked.connect(lambda: self.pan_left())
        self.view.side_menu.right_btn.clicked.connect(lambda: self.pan_right())
        self.view.side_menu.up_btn.clicked.connect(lambda: self.pan_up())
        self.view.side_menu.down_btn.clicked.connect(lambda: self.pan_down())
        self.view.side_menu.list.clicked.connect(self.object_edit)

        self.view.show()

    def window_width(self):
        return self.graphic.window["x_max"] - self.graphic.window["x_min"]

    def window_height(self):
        return self.graphic.window["y_max"] - self.graphic.window["y_min"]

    def viewport_width(self):
        return self.graphic.viewport["x_max"] - self.graphic.viewport["x_min"]

    def viewport_height(self):
        return self.graphic.viewport["y_max"] - self.graphic.viewport["y_min"]

    def string_to_obj(self, string_coords):
        coords = list(eval(string_coords))

        obj_type = ObjType(3)
        if(isinstance(coords[0], int)):
            obj_type = ObjType(1)
            coords = [(coords[0], coords[1])]
        elif(len(coords)<3):
            obj_type = ObjType(2)

        return (obj_type, coords)



    def save_object(self):

        dialog = ObjectDialog()

        if dialog.exec():
            (name, string_coords, delete) = dialog.get_inputs()

            (obj_type, coords) = self.string_to_obj(string_coords)

            obj = GraphicObject(name, obj_type, coords)
            self.graphic.objects.append(obj)

            self.draw()
            self.make_list()

    def object_edit(self, item):
        name = self.graphic.objects[item.row()].name
        coords = str(self.graphic.objects[item.row()].coords)

        dialog = ObjectDialog(None, name, coords, False)
        result = dialog.exec()
        if (result):
            (new_name, new_string_coords, delete) = dialog.get_inputs()
            if(delete):
                del self.graphic.objects[item.row()]
            else:
                (new_obj_type, new_coords) = self.string_to_obj(string_coords)
                self.graphic.objects[item.row()].name = new_name
                self.graphic.objects[item.row()].obj_type = new_obj_type
                self.graphic.objects[item.row()].coords = new_coords
        
        self.draw()
        self.make_list()



    def draw(self):
        self.view.canvas.clear_canvas()
        obj_list = []
        for ob in self.graphic.objects:
            viewport_coords = [self.graphic.viewport_transformation(point[0],point[1]) for point in ob.coords]
            self.view.canvas.draw(viewport_coords)

        self.view.canvas.update()

    def make_list(self):            
        obj_list = []
        for ob in self.graphic.objects:
            obj_list.append(ob.obj_type.name + '(' + ob.name + ')')

        self.view.side_menu.make_list(obj_list)

    def reset_multiplier(self):
        if (self.view.side_menu.step.text().strip() == ""):
            self.view.side_menu.step.setText("10")

    def zoom_in(self):
        self.reset_multiplier()
        step = int(self.view.side_menu.step.text())

        self.graphic.window["x_max"] -= int(step/2)
        self.graphic.window["y_max"] -= int(step/2)
        self.graphic.window["x_min"] += int(step/2)
        self.graphic.window["y_min"] += int(step/2)
        self.draw()

    def zoom_out(self):
        self.reset_multiplier()
        step = int(self.view.side_menu.step.text())
        
        self.graphic.window["x_max"] += int(step/2)
        self.graphic.window["y_max"] += int(step/2)
        self.graphic.window["x_min"] -= int(step/2)
        self.graphic.window["y_min"] -= int(step/2)

        self.draw()


    def pan_right(self):
        self.reset_multiplier()
        step = int(self.view.side_menu.step.text())

        self.graphic.window["x_max"] += step
        self.graphic.window["x_min"] += step

        self.draw()


    def pan_left(self):
        self.reset_multiplier()
        step = int(self.view.side_menu.step.text())

        self.graphic.window["x_max"] -= step
        self.graphic.window["x_min"] -= step

        self.draw()

    def pan_up(self):
        self.reset_multiplier()
        step = int(self.view.side_menu.step.text())

        self.graphic.window["y_max"] += step
        self.graphic.window["y_min"] += step

        self.draw()

    def pan_down(self):
        self.reset_multiplier()
        step = int(self.view.side_menu.step.text())

        self.graphic.window["y_max"] -= step
        self.graphic.window["y_min"] -= step

        self.draw()