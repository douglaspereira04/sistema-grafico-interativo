from model.graphics_2d.graphic_2d_element import Graphic2DElement
from model.obj_type import ObjType
from model.clipper import Clipper
from model.graphics_2d.transformation_2d import Transformation2D
import numpy as np

class Point2D(Graphic2DElement):
    def __init__(self, coords=(0.,0.), color="black"):
        self.coords = np.array([coords[0],coords[1], 1])
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


    def get_vertices(self):
        return [self.coords]


    """
    Retorna ponto projetado e clippado
    """
    def normalize(self, vertices = None, normalization_matrix = None, line_clipping = None, d = None, viewport_transformation_matrix = None):
        scn_coords = Transformation2D.transform_point(self.coords , normalization_matrix)
        scn_coords = Clipper.point_clipping(scn_coords)
        if(not(scn_coords is None)):
            self.viewported =  [Transformation2D.transform_point(scn_coords, viewport_transformation_matrix)]


    """
    Transforma o ponto dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        self.coords = Transformation2D.transform_point(self.coords , transformation_matrix)
