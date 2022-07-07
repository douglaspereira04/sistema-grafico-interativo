class Graphic3DObject:
    def __init__(self, name, elements=None):
        self.elements = list()
        if(elements != None):
            self.elements+=elements
        self.name = name
        self.group_center = None

    def center(self):
        sum_x = 0
        sum_y = 0
        sum_z = 0

        _len = 0

        for element in self.elements:
            element.group = self
            for vertex in element.get_vertices():
                (x,y,z, _) = vertex
                sum_x += x
                sum_y += y
                sum_z += z

            _len += len(element.get_vertices())


        centroid_x = sum_x/_len
        centroid_y = sum_y/_len
        centroid_z = sum_z/_len
        
        return (centroid_x, centroid_y, centroid_z)

    """
    Transforma todos os elementos dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        self.group_center = self.center()
        for element in self.elements:
            element.transform(transformation_matrix)

    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, transformation_list):
        self.group_center = self.center()
        for element in self.elements:
            element.transform_from_list(transformation_list)