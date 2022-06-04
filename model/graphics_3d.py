import math
import numpy as np
from enum import Enum
from model.obj_type import ObjType
from model.graphics import Graphics
from model.graphic_3d_object import Axis, Object3d
from model.point_3d import Point3d

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

class Graphics3d(Graphics):
    def __init__(self):
        super().__init__()

    vrp_vpn = Object3d(name=None, vertices=[Point3d(0,0,0),Point3d(0,0,1)], edges=None, color=None, filled=False)
   
    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, object_index, transformation_list):

        obj = self.objects[object_index]

        transformation_matrix_list = [self.get_transformation_matrix(obj, transformation) for transformation in transformation_list]
        transformation_matrix = self.get_transformation_matrix_composition(transformation_matrix_list)
        
        if(len(transformation_matrix)>0):
            obj.transform(transformation_matrix)

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
    def get_transformation_matrix(self, obj, transformation):

        #SCALING (OBJ CENTER)
        if (transformation[0] == TransformationType.SCALING):
            factor = transformation[1]
            return obj.scaling_matrix(factor,factor,factor)
        #ROTATION
        elif (transformation[0] == TransformationType.ROTATION):
            (_type,degrees,x,y,z,_axis) = transformation[1]
            #WORLD
            if(transformation[1][0] == RotationType.WORLD_CENTER):
                return obj.rotation_matrix(transformation[1][5], transformation[1][1])
            #OBJECT
            if (transformation[1][0] == RotationType.OBJECT_CENTER):
                return obj.rotation_object_center_matrix(transformation[1][5], transformation[1][1])
            #POINT
            if (transformation[1][0] == RotationType.GIVEN_POINT):
                return rotation_point_matrix(self, axis, degrees, x, y ,z)
        #TRANSLATION
        elif (transformation[0] == TransformationType.TRANSLATION):
            (x,y,z) = transformation[1]
            return self.translation_matrix(x,y,z)

        return None


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
    Clip de objetos Sutherland-Hodgman
    com clip de linhas Cohen-Sutherland
    """
    def sutherland_hodgman_clipping(self, polygon):
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
                    scn_clipped_coords = self.sutherland_hodgman_clipping(scn_coords)

                    if(scn_clipped_coords != None):
                        if(obj.filled):
                            scn_clipped_coords.append(scn_clipped_coords[0])
                            
                        display.append((scn_clipped_coords, obj.color, obj.filled))
            else:
                #caso o clipping esteja desativado
                display.append((scn_coords, obj.color, obj.filled))


        self.display = display


    def parallel_projection(self):
        vrp = vrp_vpn.vertices[0]
        (vrp_x, vrp_y, vrp_z) = (vrp.x,vrp.y,vrp.z)
        vpn = vrp_vpn.vertices[1]
        (vpn_x, vpn_y, vpn_z) = (vpn.x,vpn.y,vpn.z)

        rotation_x_angle = math.atan(math.sqrt(((vpn_x-vrp_x)**2+(vpn_y-vrp_y)**2)/(vpn_z-vrp_z)))
        rotation_x_angle = math.atan(math.sqrt(((vpn_x-vrp_x)**2+(vpn_z-vrp_z)**2)/(vpn_y-vrp_y)))
        rotation_x_angle = math.atan(math.sqrt(((vpn_y-vrp_y)**2+(vpn_z-vrp_z)**2)/(vpn_x-vrp_x)))

        vrp_vpn.transform(vrp_vpn.translation_matrix(vrp_x, vrp_y, vrp_z))


