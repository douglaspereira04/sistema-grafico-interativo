from model.graphic_object import GraphicObject
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType

class WireframeObject(GraphicObject):
    def __init__(self, name=None, coords=[], color="black", filled=False):
        super().__init__(name, ObjType.WIREFRAME, coords, color, filled)


    def center(self):
        sum_x = 0
        sum_y = 0

        last_point = None

        _len = len(self.coords)
        if(self.coords[0] == self.coords[_len-1] and _len > 1):
            _len-=1

        for i in range(_len):
            sum_x += self.coords[i][0]
            sum_y += self.coords[i][1]

        centroid_x = sum_x/_len
        centroid_y = sum_y/_len
        return (centroid_x, centroid_y)

    def clip(self):
        if(not self.filled):
            return Clipper.line_set_clipping(self.scn, LineClipping.COHEN_SUTHERLAND)
        else:
            return Clipper.sutherland_hodgman_clipping(self.scn)