from model.clipper import Clipper
from model.transformation_3d import Transformation3D

class GraphicObject:
    def __init__(self, name=None, obj_type=None,coords=[], color="black", filled=False):
        self.name = name
        self.obj_type = obj_type
        self.coords = coords
        self.color = color
        self.filled = filled

    def center(self):
        pass

    """
    Transforma todos os pontos dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        Transformation3D.transform(self.coords, transformation_matrix)

    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, transformation_list):
        center = self.center()

        transformation_matrix_list = [self.get_transformation_matrix(transformation, center) for transformation in transformation_list]
        transformation_matrix = Transformation3D.compose_matrix(transformation_matrix_list)

        self.transform(transformation_matrix)

    def project(self):
        pass