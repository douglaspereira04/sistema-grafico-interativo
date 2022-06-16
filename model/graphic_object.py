from model.clipper import Clipper
from model.transformation_3d import Transformation3D, Transformation3DType, Rotation3DType

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
    Traduz um objeto que representa uma transformação 
    para a matriz de transformação correspondente
    """
    def get_transformation_matrix(self, transformation, center):

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
        center = self.center()

        transformation_matrix_list = [self.get_transformation_matrix(transformation, center) for transformation in transformation_list]
        transformation_matrix = Transformation3D.compose_matrix(transformation_matrix_list)

        self.transform(transformation_matrix)

    def project(self):
        pass