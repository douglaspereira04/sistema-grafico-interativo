from model.graphics_3d.graphic_3d_element import Graphic3DElement
from model.obj_type import ObjType
from model.clipper import Clipper
from model.graphics_3d.transformation_3d import Transformation3D
import numpy as np

class Point3D(Graphic3DElement):
    def __init__(self, coords=(0.,0.,0.), color="black"):
        self.coords = np.array([coords[0],coords[1],coords[2], 1])
        super().__init__(obj_type=ObjType.POINT, color=color)

    def __str__(self):
        return str(tuple(self.coords[:-1]))

    def __repr__(self):
        return self.__str__()

    def center(self):
        return self.coords[:-1]

    def __getitem__(self, key):
        return self.coords[key]

    def __index__(self):
        return self.coords

    def set_coords(self,coords):
        self.coords[0] = coords[0]
        self.coords[1] = coords[1]
        self.coords[2] = coords[2]


    def get_vertices(self):
        return [self.coords]


    """
    Retorna ponto projetado e clippado
    """
    def project(self, vertices = None, projection_matrix = None, line_clipping = None, d = None, viewport_transformation_matrix = None):
        [x,y,z,w] = Transformation3D.transform_point(self.coords , projection_matrix)
        coords = np.array([x/w, y/w, 1])
        coords = Clipper.point_clipping(coords)
        if(not(coords is None)):
            self.viewported =  [Transformation3D.transform_point(coords, viewport_transformation_matrix)]


    """
    Transforma o ponto dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        self.coords = Transformation3D.transform_point(self.coords , transformation_matrix)
