from model.graphic_element import GraphicElement
from model.obj_type import ObjType
from model.clipper import Clipper
from model.transformation_3d import Transformation3D
from model.transformation import Transformation

class Point3D(GraphicElement):
    def __init__(self, coords=None, color="black"):
        point = list()
        if(coords != None):
            point.append(coords)
        super().__init__(obj_type=ObjType.POINT, points=point, color=color)

    def __str__(self):
        return str(self.get_coords())

    def get_vertices(self):
        return self.points

    def center(self):
        return self.points[0]

    def get_coords(self):
        return self.points[0]

    def set_coords(self,coords):
        self.points = list()
        self.points.append(coords)

    def project(self, projection_matrix):
        (x,y,z) = self.get_coords()
        coord = (x,y,z,1)
        (x,y,z,w) = Transformation3D.transform_point(coord, projection_matrix)
        scn_coord = (x/w, y/w)

        return Clipper.point_clipping([scn_coord])

    """
    Transforma todos os pontos dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        transformed_point = Transformation3D.transform_3d_point(self.get_coords(), transformation_matrix)
        self.set_coords(transformed_point)
