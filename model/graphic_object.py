from model.transformation import TransformationType, RotationType, Transformation
from model.clipper import Clipper

class GraphicObject:
    def __init__(self, name=None, obj_type=None,coords=[], color="black", filled=False):
        self.name = name
        self.obj_type = obj_type
        self.coords = coords
        self.color = color
        self.filled = filled
        self.scn = None

    def center(self):
        pass

    """
    Transforma todos os pontos dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        Transformation.transform(self.coords, transformation_matrix)

    """
    Traduz um objeto que representa uma transformação 
    para a matriz de transformação correspondente
    """
    def get_transformation_matrix(self, transformation, center):

        if (transformation.transformation_type == TransformationType.ROTATION):
            if(transformation.rotation_type == RotationType.OBJECT_CENTER):
                return transformation.get_matrix(center[0], center[1])


        if (transformation.transformation_type == TransformationType.SCALING):
            return transformation.get_matrix(center[0], center[1])

        return transformation.get_matrix()


    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, transformation_list):
        center = self.center()

        transformation_matrix_list = [self.get_transformation_matrix(transformation, center) for transformation in transformation_list]
        transformation_matrix = Transformation.compose_matrix(transformation_matrix_list)

        self.transform(transformation_matrix)

    def normalize(self, normalization_matrix):
        self.scn = self.coords.copy()
        Transformation.transform(self.scn, normalization_matrix)
        return self.scn

    def clip(self):
        pass