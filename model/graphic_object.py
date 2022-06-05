from model.transformation import TransformationType, RotationType, Transformation

class GraphicObject:
    def __init__(self, name=None, obj_type=None,coords=[], color="black", filled=False):
        self.name = name
        self.obj_type = obj_type
        self.coords = coords
        self.color = color
        self.filled = filled
        self.center = None

    def centroid(self):
        sum_x = 0
        sum_y = 0

        last_point = None

        _len = len(self.coords)
        if(self.coords[0] == self.coords[_len-1] and _len > 1):
            _len-=1

        for i in range(_len):
            sum_x += self.coords[i][0]
            sum_y += self.coords[i][1]

        centroid_x = sum_x/_len
        centroid_y = sum_y/_len
        return (centroid_x, centroid_y)

    """
    Transforma todos os pontos dado uma matriz de transformação
    Recalcula o centroid
    """
    def transform(self, transformation_matrix):
        Transformation.transform(self.coords, transformation_matrix)

    """
    Traduz um objeto que representa uma transformação 
    para a matriz de transformação correspondente
    """
    def get_transformation_matrix(self, transformation):
        if (transformation.transformation_type == TransformationType.ROTATION):
            if(transformation.rotation_type == RotationType.OBJECT_CENTER):
                return transformation.get_matrix(self.center[0], self.center[1])


        if (transformation.transformation_type == TransformationType.SCALING):
            return transformation.get_matrix(self.center[0], self.center[1])

        return transformation.get_matrix()


    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, transformation_list):
        self.center = self.centroid()

        transformation_matrix_list = [self.get_transformation_matrix(transformation) for transformation in transformation_list]
        transformation_matrix = Transformation.compose_matrix(transformation_matrix_list)

        self.transform(transformation_matrix)

        self.center = self.centroid()
        
