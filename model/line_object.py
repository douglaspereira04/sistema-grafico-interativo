from model.graphic_object import GraphicObject
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType

class LineObject(GraphicObject):
    def __init__(self, name=None, coords=[], color="black"):
        super().__init__(name, ObjType.LINE, coords, color, False)


    def center(self):
        [p0,p1] = self.coords
        xm = (p0[0]+p1[0])/2
        ym = (p0[1]+p1[1])/2

        return (xm, ym)

    def clip(self, line_clipping):
        if(line_clipping == LineClipping.LIAN_BARSK):
            return Clipper.lian_barsk_clipping(self.scn)
        else:
            return Clipper.cohen_sutherland_clipping(self.scn)