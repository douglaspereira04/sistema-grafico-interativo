from model.graphic_object import GraphicObject
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType
from model.transformation import Transformation
from model.transformation_3d import Transformation3D

class WireframeObject(GraphicObject):
    def __init__(self, name=None, coords=[], color="black"):
        super().__init__(name, ObjType.WIREFRAME, coords, color, False)

    def center(self):
        sum_x = 0
        sum_y = 0
        sum_z = 0

        _len = len(self.coords)

        for i in range(_len):
            sum_x += self.coords[i][0]
            sum_y += self.coords[i][1]
            sum_z += self.coords[i][2]

        centroid_x = sum_x/_len
        centroid_y = sum_y/_len
        centroid_z = sum_z/_len
        return (centroid_x, centroid_y, centroid_z)

    def project(self, projection_matrix, normalization_matrix, line_clipping):
        projected_coords = []
        for i in range(0,len(self.coords),2):

            projected_3d_coord = Transformation3D.transform_point(self.coords[i], projection_matrix)
            projected_coord = (projected_3d_coord[0], projected_3d_coord[1])
            scn_coord_0 = Transformation.transform_point(projected_coord, normalization_matrix)

            projected_3d_coord = Transformation3D.transform_point(self.coords[i+1], projection_matrix)
            projected_coord = (projected_3d_coord[0], projected_3d_coord[1])
            scn_coord_1 = Transformation.transform_point(projected_coord, normalization_matrix)

            clipped = None
            if(line_clipping == LineClipping.LIAN_BARSK):
                clipped = Clipper.lian_barsk_clipping([scn_coord_0, scn_coord_1])
            else:
                clipped = Clipper.cohen_sutherland_clipping([scn_coord_0, scn_coord_1])

            if(clipped != None):
                projected_coords += clipped


        self.clipped_scn = projected_coords

        return self.clipped_scn