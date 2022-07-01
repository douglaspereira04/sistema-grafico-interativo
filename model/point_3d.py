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

    def __repr__(self):
        return self.__str__()

    def get_vertices(self):
        return self.points

    def center(self):
        return self.points[0]

    def get_coords(self):
        return self.points[0]

    def __getitem__(self, key):
        return self.points[0][key]

    def __index__(self):
        return self.get_coords

    def set_coords(self,coords):
        self.points = list()
        self.points.append(coords)

    def project(self, projection_matrix, viewport_transformation_matrix):
        (x,y,z,w) = Transformation3D.transform_point(self.get_coords(), projection_matrix)
        scn_coord = (x/w, y/w)
        clipped_coords = Clipper.point_clipping([scn_coord])

        if(clipped_coords != None):
            return [self.get_display_object(clipped_coords, viewport_transformation_matrix)]
        return None

    """
    Transforma todos os pontos dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        transformed_point = Transformation3D.transform_3d_point(self.get_coords(), transformation_matrix)
        self.set_coords(transformed_point)
