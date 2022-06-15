from model.graphic_object import GraphicObject
from model.obj_type import ObjType
from model.clipper import Clipper
from model.transformation_3d import Transformation3D

class PointObject(GraphicObject):
    def __init__(self, name=None, coords=[], color="black"):
        super().__init__(name, ObjType.POINT, coords, color, False)


    def center(self):
        return self.coords[0]


    def project(self, projection_matrix, normalization_matrix):
        projected_3d_coord = Transformation3D.transform_point(self.coords[0], projection_matrix)
        projected_coord = (projected_3d_coord[0], projected_3d_coord[1])
        scn_coord = Transformation3D.transform_point(projected_coord, normalization_matrix)
        return Clipper.point_clipping(scn_coord)
