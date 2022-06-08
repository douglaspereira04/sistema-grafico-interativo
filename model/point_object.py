from model.graphic_object import GraphicObject
from model.obj_type import ObjType
from model.clipper import Clipper

class PointObject(GraphicObject):
    def __init__(self, name=None, coords=[], color="black"):
        super().__init__(name, ObjType.POINT, coords, color, False)


    def center(self):
        return self.coords[0]

    def clipped(self):
        return Clipper.point_clipping(self.scn)
