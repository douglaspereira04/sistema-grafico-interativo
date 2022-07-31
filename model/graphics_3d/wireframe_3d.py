from model.graphics_3d.graphic_3d_element import Graphic3DElement
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType
from model.graphics_3d.transformation_3d import Transformation3D
import numpy as np

class Wireframe3D(Graphic3DElement):
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
        sum_z = 0

        _len = len(self.vertices)

        for i in range(_len):
            (x,y,z, _) = self.vertices[i]
            sum_x += x
            sum_y += y
            sum_z += z

        centroid_x = sum_x/_len
        centroid_y = sum_y/_len
        centroid_z = sum_z/_len
        return (centroid_x, centroid_y, centroid_z)

    """
    Transforma todos os vertices dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        for i in range(len(self.vertices)):
            self.vertices[i] = Transformation3D.transform_point(self.vertices[i], transformation_matrix)


    def project(self, vertices = None, projection_matrix = None, line_clipping = None, d = None, viewport_transformation_matrix = None):
        if(vertices is None):
            self.project(self.vertices, projection_matrix, line_clipping, d, viewport_transformation_matrix) 
        else:
            projected_coords = []

            if(not self.filled):

                if(line_clipping == LineClipping.LIAN_BARSK):
                    clipper = Clipper.lian_barsk_clipping
                else:
                    clipper = Clipper.cohen_sutherland_clipping

                p0 = Transformation3D.project_point(vertices[0], projection_matrix)
                for i in range(len(vertices)-1):
                    p1 = Transformation3D.project_point(vertices[i+1], projection_matrix)

                    clipped = clipper([p0, p1])
                    if(not (clipped is None)):
                        [v0, v1] = clipped
                        v0 = np.array([v0[0], v0[1],1])
                        v1 = np.array([v1[0], v1[1],1])
                        v0 =  Transformation3D.transform_point(v0, viewport_transformation_matrix)
                        v1 =  Transformation3D.transform_point(v1, viewport_transformation_matrix)
                        projected_coords.append([v0, v1])

                    p0 = p1
            else:

                projected_coords = [Transformation3D.project_point(v, projection_matrix) for v in vertices]
                projected_coords = Clipper.sutherland_hodgman_clipping(projected_coords)
                if(not (projected_coords is None)):
                    projected_coords =  [Transformation3D.transform_point(np.array([p[0], p[1],1.0]), viewport_transformation_matrix) for p in projected_coords]

            self.viewported =  projected_coords