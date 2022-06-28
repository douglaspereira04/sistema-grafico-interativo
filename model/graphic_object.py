class GraphicObject:
    def __init__(self, name, elements=None):
        self.elements = list()
        if(elements != None):
            self.elements+=elements
        self.name = name


    """
    Transforma todos os elementos dado uma matriz de transformação
    """
    def transform(self, transformation_matrix):
        for element in self.elements:
            element.transform(transformation_matrix)

    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, transformation_list):
        for element in self.elements:
            element.transform_from_list(transformation_list)