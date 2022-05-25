import math
import numpy as np
from enum import Enum
from model.obj_type import ObjType

class RotationType(Enum):
    OBJECT_CENTER = 1
    WORLD_CENTER = 2
    GIVEN_POINT = 3

class TransformationType(Enum):
    TRANSLATION = 1
    SCALING = 2
    ROTATION = 3

class RegionCode(Enum):
    INSIDE = 0b0000
    LEFT = 0b0001
    RIGHT = 0b0010
    BOTTOM = 0b0100
    TOP = 0b1000

class LineClipping(Enum):
    COHEN_SUTHERLAND = 0
    LIAN_BARSK = 1

class Graphics:
    def __init__(self):
        self.objects = []

        self.display = []

        """
        Os valores de viewport e window são inicializados com 0
        mas são atualizados pelo controller para serem compatíveis
        com o tamanho da interface. O controller ajustará inicialmente o 
        tamanho da window igual o tamanho da viewport
        """
        self.viewport = {
            "x_max": 0, 
            "x_min": 0,
            "y_max": 0, 
            "y_min": 0
        }
        self.window = {
            "x_max": 0, 
            "x_min": 0,
            "y_max": 0, 
            "y_min": 0
        }

        self.zoom = 1
        self.vup_angle = 0
        self.border = 20
        self.line_clipping = LineClipping.LIAN_BARSK
        self.enable_clipping = True

    def window_width(self):
        return self.window["x_max"] - self.window["x_min"]

    def window_height(self):
        return self.window["y_max"] - self.window["y_min"]

    def viewport_width(self):
        return self.viewport["x_max"] - self.viewport["x_min"]

    def viewport_height(self):
        return self.viewport["y_max"] - self.viewport["y_min"]

    def window_aspect_ratio(self):
        return self.window_width()/self.window_height()

    def viewport_aspect_ratio(self):
        return self.window_width()/self.window_height()


    def window_center(self):
        x = (self.window["x_max"] + self.window["x_min"] )/2
        y = (self.window["y_max"] + self.window["y_min"] )/2

        return (x,y)

    def set_window_height(self, height, center, aspect):
        (x,y) = center
        half_height = (height/2)
        self.window["y_min"] = y - half_height
        self.window["y_max"] = y + half_height

        half_width = (height*aspect)/2

        self.window["x_min"] = x - half_width
        self.window["x_max"] = x + half_width

    def set_window_width(self, width, center, aspect):

        (x,y) = center
        half_width = (width/2)
        self.window["x_min"] = x - half_width
        self.window["x_max"] = x + half_width

        half_height = (width/aspect)/2
        self.window["y_min"] = y - half_height
        self.window["y_max"] = y + half_height


    """
    Define o tamanho da window, mantendo a proporção da window anterior
    """
    def set_window(self,window):
        aspect = self.window_aspect_ratio()
        (center,dimension) = window
        (x,y) = center
        (width,height) = dimension

        self.set_window_width(width,center,aspect)

        if(self.window_height() < height):
            self.set_window_height(height,center,aspect)

    """
    A seguir são as funções que de navegação. Elas se orientam a um valor de passo, definido no parametro "step".
    A função zoom_in diminui a window, limitando a um tamanho maior que zero e zoom_out aumenta a window.
    As funções de panning movem a window considerando o angulo em que ela está rotacionada, 
    ou seja, o angulo de view up vector 
    """
    def zoom_in(self, step):
        aspect = self.window_aspect_ratio()

        xmax = self.window["x_max"] - ((step/2)*aspect)
        ymax = self.window["y_max"] - (step/2)
        xmin = self.window["x_min"] + ((step/2)*aspect)
        ymin = self.window["y_min"] + (step/2)

        if (((xmax - xmin )<= 0) or ((ymax - ymin) <= 0)):

            return False
        else:
            self.window["x_max"] = xmax
            self.window["y_max"] = ymax
            self.window["x_min"] = xmin
            self.window["y_min"] = ymin
            
            return True


    def zoom_out(self, step):
        aspect = self.window_aspect_ratio()

        self.window["x_max"] += (step/2)*aspect
        self.window["y_max"] += (step/2)
        self.window["x_min"] -= (step/2)*aspect
        self.window["y_min"] -= (step/2)


    def pan_right(self, step):
        _sin = (math.sin(math.radians(self.vup_angle)))
        _cos = (math.cos(math.radians(self.vup_angle)))

        self.window["x_max"] += _cos*step
        self.window["x_min"] += _cos*step
        self.window["y_max"] -= _sin*step
        self.window["y_min"] -= _sin*step


    def pan_left(self, step):
        _sin = (math.sin(math.radians(self.vup_angle)))
        _cos = (math.cos(math.radians(self.vup_angle)))

        self.window["x_max"] -= _cos*step
        self.window["x_min"] -= _cos*step
        self.window["y_max"] += _sin*step
        self.window["y_min"] += _sin*step

    def pan_up(self, step):
        _sin = (math.sin(math.radians(self.vup_angle)))
        _cos = (math.cos(math.radians(self.vup_angle)))

        self.window["y_max"] += _cos*step
        self.window["y_min"] += _cos*step
        self.window["x_max"] += _sin*step
        self.window["x_min"] += _sin*step

    def pan_down(self, step):
        _sin = (math.sin(math.radians(self.vup_angle)))
        _cos = (math.cos(math.radians(self.vup_angle)))

        self.window["y_max"] -= _cos*step
        self.window["y_min"] -= _cos*step
        self.window["x_max"] -= _sin*step
        self.window["x_min"] -= _sin*step

    """
    Funções que retorna transformações
    Usadas nos atalhos de transformação
    """
    def translation(self, x, y):
        return (TransformationType.TRANSLATION, (x, y))

    def scale(self, scale):
        return (TransformationType.SCALING, scale)

    def natural_rotation(self, degrees, centroid):
        (x,y) = centroid
        return (TransformationType.ROTATION, (RotationType.OBJECT_CENTER, degrees, x, y))

    """
    Funções que criam e retornam matrizes de transformação
    daos parametros
    """
    def translation_matrix(self, x, y):
        return [[1.0,  0.,  0.],[ 0,  1.0,  0.],[ x,  y,  1.]]

    def scaling_matrix(self, x, y):
        return [[x,  0.,  0.],[ 0,  y,  0.],[ 0., 0., 1.]]

    def rotation_matrix(self, degrees):
        _sin = (math.sin(math.radians(degrees)))
        _cos = (math.cos(math.radians(degrees)))

        return [[ _cos,  -_sin,  0.],[ _sin,  _cos,  0.],[ 0.,  0.,  1.]]

    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, object_index, transformation_list):

        coords = self.objects[object_index].coords
        centroid = self.objects[object_index].centroid()

        transformation_matrix_list = [self.get_transformation_matrix(transformation,centroid) for transformation in transformation_list]
        transformation_matrix = self.get_transformation_matrix_composition(transformation_matrix_list)
        
        if(len(transformation_matrix)>0):
            for i in range(len(coords)):
                coords[i] = self.transform(coords[i], transformation_matrix)

    """
    Dada uma lista de matrizes de transformação
    retorna a matriz resultante
    """
    def get_transformation_matrix_composition(self, transformation_matrix_list):
        
        transformation_matrix_composition = []
        if(len(transformation_matrix_list) > 0):
            transformation_matrix_composition = transformation_matrix_list[0]

            for i in range(len(transformation_matrix_list)-1):
                transformation_matrix_composition = np.matmul(transformation_matrix_composition,transformation_matrix_list[i+1])

        return transformation_matrix_composition

    """
    Traduz um objeto que representa uma transformação 
    para a matriz de transformação correspondente
    """
    def get_transformation_matrix(self, transformation,centroid):

        #SCALING (OBJ CENTER)
        if (transformation[0] == TransformationType.SCALING):
            parcial = np.matmul(self.translation_matrix(-centroid[0], -centroid[1]),self.scaling_matrix(transformation[1],transformation[1]))
            return np.matmul(parcial,self.translation_matrix(centroid[0], centroid[1]))
        #ROTATION
        if (transformation[0] == TransformationType.ROTATION):
            #WORLD
            if(transformation[1][0] == RotationType.WORLD_CENTER):
                return self.rotation_matrix(transformation[1][1])
            #OBJECT
            if (transformation[1][0] == RotationType.OBJECT_CENTER):
                parcial = np.matmul(self.translation_matrix(-centroid[0], -centroid[1]),self.rotation_matrix(transformation[1][1]))
                return np.matmul(parcial,self.translation_matrix(centroid[0], centroid[1]))
            #POINT
            if (transformation[1][0] == RotationType.GIVEN_POINT):
                parcial = np.matmul(self.translation_matrix(-transformation[1][2], -transformation[1][3]),self.rotation_matrix(transformation[1][1]))
                return np.matmul(parcial, self.translation_matrix(transformation[1][2], transformation[1][3]))
        #TRANSLATION
        if (transformation[0] == TransformationType.TRANSLATION):
            return self.translation_matrix(transformation[1][0],transformation[1][1])

    """
    Retorna o ponro transformado dado um ponto e uma matriz de transformação
    """
    def transform(self, point, transformation_matrix):
        (x,y) = point
        [x1,y1,z1] = np.matmul([x,y,1],transformation_matrix)
        return (x1,y1)
        

    """
    Retorna a matriz de normalização para as configurações 
    atuais da window
    """
    def normalization_matrix(self):
        (x_center, y_center) = self.window_center()
        translation_matrix = self.translation_matrix(-x_center,-y_center)

        rotation_matrix = self.rotation_matrix(-self.vup_angle)

        scale_x = 1/(self.window_width()/2)
        scale_y = 1/(self.window_height()/2)

        scaling_matrix = self.scaling_matrix(scale_x,scale_y)

        normalization_matrix = np.matmul(np.matmul(translation_matrix,rotation_matrix),scaling_matrix)
        return  normalization_matrix


    """
    Transformação para viewport
     - Ajustado para a representação em sistema de coordenadas normalizado
     - Ajustado para clippling
    """
    def viewport_transformation(self, x, y):
        x1 = ((x- -1) * (self.viewport_width() - (self.border*2)) / 2) + self.border
        y1 = ((1 - ((y - -1) / 2)) * (self.viewport_height() - (self.border*2))) + self.border
        return (x1,y1)

    """
    Clip de ponto no espaço normalizado da window
    Retorna None se o ponto não faz parte 
    da àrea da window
    """
    def point_clipping(self, point):
        """
        Point deve ser uma lista 
        com uma única tupla com as coordenadas
        do ponto
        """
        (x,y) = point[0]

        if(x < 1 and x > -1 and y < 1 and y > -1):
            return point
        else:
            return None

    """
    Clip de linha no espaço normalizado da window
    com o algorítimo Cohen-Sutherland
    Retorna None se não existe segmento de reta
    que faz parte da àrea da window
    """
    def cohen_sutherland_clipping(self, line):
        """
        Line deve ser uma lista com dois pontos.
        Cada ponto deve ser uma tupla com as coordanadas.
        """
        [initial, final] = line

        clipped = None

        initial_rc = self.region_code(initial)
        final_rc = self.region_code(final)


        (x0,y0) = initial
        (x1,y1) = final


        while ((initial_rc & final_rc) == 0b0000):
            """
            Se os dois pontos, ou os dois pontos depois de algum recálculo
            que coloca os limites sobre as bordas,
            se encontrarem fora da região central e na mesma região
            clipped == None.
            Se ele se encontrarem ambos na região central
            então foi encontrada o novo segmento de reta.
            """

            if(initial_rc == 0b0000 and final_rc == 0b0000):
                clipped = [initial, final]
                break

            #Calcula a intersecção e reatribui, recalculando a regiao
            if(initial_rc != RegionCode.INSIDE.value):
                initial =  self.cohen_sutherland_intersect(initial, final, initial_rc)
                initial_rc = self.region_code(initial)

            elif(final_rc != RegionCode.INSIDE.value):
                final =  self.cohen_sutherland_intersect(final, initial, final_rc)
                final_rc = self.region_code(final)


        return clipped

    """
    Calcula a intersecção de uma reta com a borda da window, 
    dados dois pontos e uma regiao.
    """
    def cohen_sutherland_intersect(self, vertex_1, vertex_2, region):
        (x0,y0) = vertex_1
        (x1,y1) = vertex_2

        #Recalcula o ponto para os extremos
        if((region & RegionCode.LEFT.value) != 0b0000):
            m = (y1-y0)/(x1-x0)
            y0 = (m*(-1 - x0)) + y0
            x0 = -1
        elif((region & RegionCode.RIGHT.value) != 0b0000):
            m = (y1-y0)/(x1-x0)
            y0 = ( m*(1 - x0)) + y0
            x0 = 1
        if((region & RegionCode.TOP.value) != 0b0000):
            m = (x1-x0)/(y1-y0)
            x0 = x0 + m*(1 - y0)
            y0 = 1
        elif((region & RegionCode.BOTTOM.value) != 0b0000):
            m = (x1-x0)/(y1-y0)
            x0 = x0 + m*(-1 - y0)
            y0 = -1

        return (x0,y0)

    """
    Calculates region code given a point

    1001|1000|1010
    ____|____|____
    0001|0000|0010
    ____|____|____
        |    |
    0101|0100|0110
    """
    def region_code(self,point):
        (x,y) = point
        rc = 0
        if(x < -1):
            rc = rc | RegionCode.LEFT.value
        if(x > 1):
            rc = rc | RegionCode.RIGHT.value
        if(y < -1):
            rc = rc | RegionCode.BOTTOM.value
        if(y > 1):
            rc = rc | RegionCode.TOP.value

        return rc


    """
    Clip de linha no espaço normalizado da window
    com o algorítimo de Lian-Barsk
    Retorna None se não existe segmento de reta
    que faz parte da àrea da window
    """
    def lian_barsk_clipping(self, line):
        """
        Line deve ser uma lista com dois pontos.
        Cada ponto deve ser uma tupla com as coordanadas.
        """
        [initial, final] = line
        (x0,y0) = initial
        (x1,y1) = final

        p1 = -(x1 - x0)
        p2 = -p1
        p3 = -(y1 - y0)
        p4 = -p3
        
        q1 = x0 - (-1)
        q2 = 1 - x0
        q3 = y0 - (-1)
        q4 = 1 - y0
        
        if ((p1 == 0 and q1 < 0) or (p2 == 0 and q2 < 0) or (p3 == 0 and q3 < 0) or (p4 == 0 and q4 < 0)):
            return None

        p = [p1,p2,p3,p4]
        q = [q1,q2,q3,q4]

        pq = [(p1,q1),(p2,q2),(p3,q3),(p4,q4)]

        neg_p_r = [qk/pk for (pk,qk) in pq if pk != 0 and pk < 0]
        pos_p_r = [qk/pk for (pk,qk) in pq if pk != 0 and pk > 0]
        
        neg_p_r.append(0)
        pos_p_r.append(1)
        
        zeta1 = max(neg_p_r)
        zeta2 = min(pos_p_r)

        if(zeta1 > zeta2):
            return None
        
        (new_x0, new_y0) = initial
        (new_x1, new_y1) = final
        
        if(zeta1 > 0):
            new_x0 = x0 + zeta1*(x1-x0)
            new_y0 = y0 + zeta1*(y1-y0)
        
        if(zeta2 < 1):
            new_x1 = x0 + zeta2*(x1-x0)
            new_y1 = y0 + zeta2*(y1-y0)
        
        return [(new_x0,new_y0),(new_x1,new_y1)]


    """
    Clip de objetos Sutherland-Hodgeman
    com clip de linhas Cohen-Sutherland
    """
    def sutherland_hodgeman_clipping(self, polygon):
        clipping_polygon = polygon.copy()
        length = 0
        intersection_list = []
        clipping_polygon_edges = []

        regions = [RegionCode.LEFT, RegionCode.RIGHT, RegionCode.TOP, RegionCode.BOTTOM]

        clipped = polygon.copy()
        curr_clip = None

        for region in regions:
            curr_clip = clipped.copy()
            length = len(curr_clip)
            clipped = []

            for i in range(length):

                curr = curr_clip[i]
                prev = curr_clip[(i - 1) % length]


                """
                Clipa a linha com cohen sutherland
                """
                curr_rc = self.region_code(curr)
                prev_rc = self.region_code(prev)
                
                if((curr_rc & region.value) == 0b0000):
                    #curr está dentro
                    if((prev_rc & region.value) != 0b0000):
                        #curr está dentro e prev está fora
                        intersect =  self.cohen_sutherland_intersect(curr, prev, region.value)
                        clipped.append(intersect)

                    #já que está dentro, fica
                    clipped.append(curr)
                elif((prev_rc & region.value) == 0b0000):
                    #curr está fora e prev está dentro
                    intersect =  self.cohen_sutherland_intersect(prev, curr, region.value)
                    clipped.append(intersect)

                    #curr é "eliminado"
                    """
                    Apesar de prev estar dentro seu valor não é adicionado agora,
                    pois esse vértice foi adicionado quando foi atribuído à curr,
                    na iteração anterior
                    """


        if(len(clipped) == 0):
            clipped = None
        return clipped


    """
    Normaliza e clipa pontos e linhas
    """
    def normalize_and_clip(self):
        display = []

        normalization_matrix = self.normalization_matrix()
        for obj in self.objects:
            scn_coords = []
            scn_clipped_coords = None

            for coords in obj.coords:
                #normalização
                new_coords = self.transform(coords,normalization_matrix)
                scn_coords.append(new_coords)

            if(self.enable_clipping == True):
                #clipping

                if(obj.obj_type == ObjType.POINT):
                    scn_clipped_coords = self.point_clipping(scn_coords)

                    if(scn_clipped_coords != None):
                        display.append((scn_clipped_coords, obj.color))
                elif(obj.obj_type == ObjType.LINE):
                    if(self.line_clipping == LineClipping.LIAN_BARSK):
                        scn_clipped_coords = self.lian_barsk_clipping(scn_coords)
                    else:
                        scn_clipped_coords = self.cohen_sutherland_clipping(scn_coords)

                    if(scn_clipped_coords != None):
                        display.append((scn_clipped_coords, obj.color))
                elif(obj.obj_type == ObjType.WIREFRAME):
                    scn_clipped_coords = self.sutherland_hodgeman_clipping(scn_coords)

                    if(scn_clipped_coords != None):
                        scn_clipped_coords.append(scn_clipped_coords[0])
                        display.append((scn_clipped_coords, obj.color))
            else:
                #caso o clipping esteja desativado
                if(obj.obj_type == ObjType.WIREFRAME):
                    scn_coords.append(scn_coords[0])
                display.append((scn_coords, obj.color))


        self.display = display