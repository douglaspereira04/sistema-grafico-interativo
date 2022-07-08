from model.clipper import Clipper
from model.graphics_2d.transformation_2d import Transformation2D, Transformation2DType, Rotation2DType
import uuid
import numpy as np

class Graphic2DElement:
    def __init__(self, obj_type=None, color="black", filled=False):
        self.obj_type = obj_type
        self.color = color
        self.filled = filled
        self.id = uuid.uuid1()
        self.group = None
        self.viewported = None

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

        center = self.group.group_center

        if (transformation.transformation_type == Transformation2DType.ROTATION):
            if(transformation.rotation_type == Rotation2DType.OBJECT_CENTER):
                return transformation.get_matrix(center[0], center[1])


        if (transformation.transformation_type == Transformation2DType.SCALING):
            return transformation.get_matrix(center[0], center[1])

        return transformation.get_matrix()


    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, transformation_list):

        transformation_matrix_list = [self.get_transformation_matrix(transformation) for transformation in transformation_list]
        transformation_matrix = Transformation2D.compose_matrix(transformation_matrix_list)

        self.transform(transformation_matrix)
         

    def normalize(self, vertices = None, normalization_matrix = None, line_clipping = None, d = None, viewport_transformation_matrix = None):
        pass