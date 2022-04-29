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

        self.view.show()

    def save_object(self):

        dialog = ObjectDialog()

        if dialog.exec():
            (name, string_coords) = dialog.get_inputs()
            coords = list(eval(string_coords))

            obj_type = ObjType(3)
            if(isinstance(coords[0], int)):
                obj_type = ObjType(1)
                coords = [(coords[0], coords[1])]
            elif(len(coords)<3):
                obj_type = ObjType(2)

            obj = GraphicObject(name, obj_type, coords)
            self.graphic.objects.append(obj)

            self.draw()
            self.make_list()

    def draw(self):
        self.view.canvas.clear_canvas()
        obj_list = []
        for ob in self.graphic.objects:
            viewport_coords = [self.graphic.viewport_transformation(point[0],point[1]) for point in ob.coords]
            self.view.canvas.draw(viewport_coords)

    def make_list(self):            
        obj_list = []
        for ob in self.graphic.objects:
            obj_list.append(ob.obj_type.name + '(' + ob.name + ')')

        self.view.side_menu.make_list(obj_list)

    def reset_multiplier(self):
        if (self.view.side_menu.factor.text().strip() == ""):
            self.view.side_menu.factor.setText("10")

    def zoom_in(self):
        self.reset_multiplier()
        factor = int(self.view.side_menu.factor.text())

        self.graphic.window["x_max"] -= int(factor/2)
        self.graphic.window["y_max"] -= int(factor/2)
        self.graphic.window["x_min"] += int(factor/2)
        self.graphic.window["y_min"] += int(factor/2)
        self.draw()

    def zoom_out(self):
        self.reset_multiplier()
        factor = int(self.view.side_menu.factor.text())
        
        self.graphic.window["x_max"] += int(factor/2)
        self.graphic.window["y_max"] += int(factor/2)
        self.graphic.window["x_min"] -= int(factor/2)
        self.graphic.window["y_min"] -= int(factor/2)

        self.draw()


    def pan_right(self):
        self.reset_multiplier()
        factor = int(self.view.side_menu.factor.text())

        self.graphic.window["x_max"] += factor
        self.graphic.window["x_min"] += factor

        self.draw()


    def pan_left(self):
        self.reset_multiplier()
        factor = int(self.view.side_menu.factor.text())

        self.graphic.window["x_max"] -= factor
        self.graphic.window["x_min"] -= factor

        self.draw()

    def pan_up(self):
        self.reset_multiplier()
        factor = int(self.view.side_menu.factor.text())

        self.graphic.window["y_max"] += factor
        self.graphic.window["y_min"] += factor

        self.draw()

    def pan_down(self):
        self.reset_multiplier()
        factor = int(self.view.side_menu.factor.text())

        self.graphic.window["y_max"] -= factor
        self.graphic.window["y_min"] -= factor

        self.draw()