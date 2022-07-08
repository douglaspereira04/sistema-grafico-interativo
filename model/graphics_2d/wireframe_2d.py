from model.graphics_2d.graphic_2d_element import Graphic2DElement
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType
from model.graphics_2d.transformation_2d import Transformation2D
import numpy as np

class Wireframe2D(Graphic2DElement):
    def __init__(self, vertices=None, color="black", filled=False):
        self.vertices = list()
        if(vertices != None):
            self.vertices += vertices
        super().__init__(obj_type=ObjType.WIREFRAME, color=color, filled=filled)


    def __str__(self):
        string = ""
        for v in self.vertices:
            string += str(tuple(v[:-1])) + ","
        return string[:-1]

    def get_vertices(self):
        return self.vertices

    def center(self):
        sum_x = 0
        sum_y = 0

        _len = len(self.vertices)

        for i in range(_len):
            (x,y, _) = self.vertices[i]
            sum_x += x
            sum_y += y

        centroid_x = sum_x/_len
        centroid_y = sum_y/_len

        return (centroid_x, centroid_y)

    """
    Transforma todos os vertices dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        for i in range(len(self.vertices)):
            self.vertices[i] = Transformation2D.transform_point(self.vertices[i], transformation_matrix)


    def normalize(self, vertices = None, normalization_matrix = None, line_clipping = None, d = None, viewport_transformation_matrix = None):

        if(vertices is None):
            self.project(self.vertices, normalization_matrix, line_clipping, d, viewport_transformation_matrix) 
        else:
            viewport_points = []

            if(not self.filled):


                if(line_clipping == LineClipping.LIAN_BARSK):
                    clipper = Clipper.lian_barsk_clipping
                else:
                    clipper = Clipper.cohen_sutherland_clipping

                p0 = Transformation2D.transform_point(vertices[0], normalization_matrix)
                for i in range(len(vertices)-1):
                    p1 = Transformation2D.transform_point(vertices[i+1], normalization_matrix)

                    clipped = clipper([p0, p1])
                    if(not (clipped is None)):
                        [v0, v1] = clipped
                        v0 = np.array([v0[0], v0[1],1])
                        v1 = np.array([v1[0], v1[1],1])
                        v0 =  Transformation2D.transform_point(v0, viewport_transformation_matrix)
                        v1 =  Transformation2D.transform_point(v1, viewport_transformation_matrix)
                        viewport_points.append([v0, v1])

                    p0 = p1
            else:

                scn_vertices = [Transformation2D.transform_point(v, normalization_matrix) for v in vertices]
                scn_vertices = Clipper.sutherland_hodgman_clipping(scn_vertices)
                if(not (scn_vertices is None)):
                    viewport_points =  [Transformation2D.transform_point(np.array([p[0], p[1],1.0]), viewport_transformation_matrix) for p in viewport_points]

            self.viewported =  viewport_points