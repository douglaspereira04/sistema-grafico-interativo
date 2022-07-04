from model.clipper import Clipper
from model.transformation_3d import Transformation3D, Transformation3DType, Rotation3DType
from model.display_object import DisplayObject
import uuid
import numpy as np

class GraphicElement:
    def __init__(self, obj_type=None, color="black", filled=False):
        self.obj_type = obj_type
        self.color = color
        self.filled = filled
        self.id = uuid.uuid1()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not (self == other)

    def center(self):
        pass

    def get_vertices(self):
        pass
        
    """
    Transforma todos os pontos dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        pass

    """
    Traduz um objeto que representa uma transformação 
    para a matriz de transformação correspondente
    """
    def get_transformation_matrix(self, transformation):

        center = self.center()

        if (transformation.transformation_type == Transformation3DType.ROTATION):
            if(transformation.rotation_type == Rotation3DType.OBJECT_CENTER):
                return transformation.get_matrix(center[0], center[1], center[2])


        if (transformation.transformation_type == Transformation3DType.SCALING):
            return transformation.get_matrix(center[0], center[1], center[2])

        return transformation.get_matrix()


    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, transformation_list):

        transformation_matrix_list = [self.get_transformation_matrix(transformation) for transformation in transformation_list]
        transformation_matrix = Transformation3D.compose_matrix(transformation_matrix_list)

        self.transform(transformation_matrix)
         

    def project(self, vertices = None, projection_matrix = None, line_clipping = None, d = None, viewport_transformation_matrix = None):
        pass