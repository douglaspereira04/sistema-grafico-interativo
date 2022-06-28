from model.graphic_element import GraphicElement
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType
from model.transformation import Transformation
from model.transformation_3d import Transformation3D

class Wireframe3D(GraphicElement):
    def __init__(self, vertices=None, edges=None, color="black", filled=False):
        self.vertices = list()
        self.edges = list()
        if(vertices != None):
            self.vertices += vertices
        if(edges != None):
            self.edges += edges
        super().__init__(obj_type=ObjType.WIREFRAME, points=self.vertices, color=color, filled=filled)


    def __str__(self):
        string = ""
        for v in self.vertices:
            string += str(v) + ","
        return string[:-1]

    def get_vertices(self):
        return self.vertices

    def center(self):
        sum_x = 0
        sum_y = 0
        sum_z = 0

        _len = len(self.vertices)

        for i in range(_len):
            (x,y,z) = self.vertices[i].get_coords()
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
        for vertex in self.vertices:
            vertex.transform(transformation_matrix)


    def project(self, projection_matrix, line_clipping):
        projected_coords = []
        for edge in self.edges:
            (v0_index,v1_index) = edge
            (v0,v1) = (self.vertices[v0_index], self.vertices[v1_index])

            (x,y,z) = v0.get_coords()
            coord = (x,y,z,1)
            (x,y,z,w) = Transformation3D.transform_point(coord, projection_matrix)
            scn_coord_0 = (x/w, y/w)

            (x,y,z) = v1.get_coords()
            coord = (x,y,z,1)
            (x,y,z,w) = Transformation3D.transform_point(coord, projection_matrix)
            scn_coord_1 = (x/w, y/w)


            clipped = None
            if(line_clipping == LineClipping.LIAN_BARSK):
                clipped = Clipper.lian_barsk_clipping([scn_coord_0, scn_coord_1])
            else:
                clipped = Clipper.cohen_sutherland_clipping([scn_coord_0, scn_coord_1])

            if(clipped != None):
                projected_coords += clipped


        self.clipped_scn = projected_coords

        return self.clipped_scn