import math
import numpy as np
from model.obj_type import ObjType
from model.graphic_object import GraphicObject
from model.display_object import DisplayObject
from model.transformation_3d import Transformation3D
from model.transformation import Transformation, RotationType, Rotation, Translation
from model.clipper import LineClipping
from enum import Enum

class Axis(Enum):
    X = 1
    Y = 2
    Z = 3

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
            "width": 0,
            "height": 0
        }

        self.border = 20
        self.line_clipping = LineClipping.LIAN_BARSK
        self.enable_clipping = True
        self.default_window = None

        self.vrp = (0,0,0)
        self.vpn = (0,0,1)
        self.vup = (0,1,0)


    def window_width(self):
        return self.window["width"]

    def window_height(self):
        return self.window["height"]

    def viewport_width(self):
        return self.viewport["x_max"] - self.viewport["x_min"]

    def viewport_height(self):
        return self.viewport["y_max"] - self.viewport["y_min"]

    def window_aspect_ratio(self):
        return self.window["width"]/self.window["height"]

    def viewport_aspect_ratio(self):
        return self.window_width()/self.window_height()


    def window_center(self):
        return self.vrp

    def set_window_height(self, height, aspect):
        self.window["width"] = height*aspect
        self.window["height"] = height

    def set_window_width(self, width, aspect):
        self.window["width"] = width
        self.window["height"] = width/aspect


    def reset_window(self):
        self.set_window(self.default_window)
    """
    Define o tamanho da window, mantendo a proporção da window anterior
    """
    def set_window(self,window):
        aspect = self.window_aspect_ratio()
        (center,dimension) = window
        (width,height) = dimension

        self.set_window_width(width,aspect)

        if(self.window_height() < height):
            self.set_window_height(height,aspect)

        self.default_window = window

    def get_window(self):
        return (self.window_center(),(self.window_width(),self.window_height()))

    def rotate_view_vector(self, x,y):
        rotation = Rotation(RotationType.OBJECT_CENTER, -self.vup_angle(), 0, 0)
        rotation_matrix = rotation.get_matrix()
        return Transformation.transform_point((x,y), rotation_matrix)



    """
    A seguir são as funções que de navegação. Elas se orientam a um valor de passo, definido no parametro "step".
    A função zoom_in diminui a window, limitando a um tamanho maior que zero e zoom_out aumenta a window.
    As funções de panning movem a window considerando o angulo em que ela está rotacionada, 
    ou seja, o angulo de view up vector 
    """
    def zoom(self, step):
        aspect = self.window_aspect_ratio()

        width = self.window["width"] - step*aspect
        height = self.window["height"] - step

        if (((width )<= 0) or ((height) <= 0)):

            return False
        else:
            self.window["width"] = width
            self.window["height"] = height
            
            return True


    def pan(self, axis, steps):
        rotation_matrix = None
        if(axis == Axis.X):
            axis = np.cross(self.vpn, self.vup)
        elif(axis == Axis.Y):
            axis = self.vup
        else:
            axis = self.vpn

        translation_matrix = Transformation3D.translation_matrix(axis[0]*steps, axis[1]*steps, axis[2]*steps)

        self.vrp = Transformation3D.transform_point(self.vrp, translation_matrix)

    def rotate(self, axis, degrees):
        
        if(axis == Axis.X):
            axis = np.cross(self.vpn, self.vup)
            transformation_matrix = Transformation3D.rotation_given_axis_matrix(degrees, axis)
            self.vpn = Transformation3D.transform_point(self.vpn, transformation_matrix)
            self.vup = Transformation3D.transform_point(self.vup, transformation_matrix)

        elif(axis == Axis.Y):
            axis = self.vup
            transformation_matrix = Transformation3D.rotation_given_axis_matrix(degrees, axis)
            self.vpn = Transformation3D.transform_point(self.vpn, transformation_matrix)
        else:
            axis = self.vpn
            transformation_matrix = Transformation3D.rotation_given_axis_matrix(degrees, axis)
            self.vup = Transformation3D.transform_point(self.vup, transformation_matrix)

    def orthogonal_projection_matrix(self):
        x_angle = self.vector_angle(self.vpn, (0,0,1), (1,0,0))
        y_angle = self.vector_angle(self.vpn, (0,0,1), (0,1,0))

        rotation_x = Transformation3D.rotation_x_matrix(x_angle)
        rotation_y = Transformation3D.rotation_y_matrix(y_angle)

        return np.matmul(rotation_x,rotation_y)

    def vup_angle(self):
        return self.vector_angle(self.vup, (0,1,0), self.vpn)

    def vector_angle(self, vector0, vector1, normal):
        (x1,y1,z1) = vector0
        (x2,y2,z2) = vector1
        (xn,yn,zn) = normal

        dot = x1*x2 + y1*y2 + z1*z2
        det = x1*y2*zn + x2*yn*z1 + xn*y1*z2 - z1*y2*xn - z2*yn*x1 - zn*y1*x2
        angle = math.atan2(det, dot)

        return math.degrees(angle)


    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, object_index, transformation_list):
        self.objects[object_index].transform_from_list(transformation_list)
        

    """
    Retorna a matriz de normalização para as configurações 
    atuais da window
    """
    def normalization_matrix(self):
        (x_center, y_center, _) = self.window_center()
        translation_matrix = Transformation.translation_matrix(-x_center,-y_center)

        rotation_matrix = Transformation.rotation_matrix(-self.vup_angle())

        scale_x = 1/(self.window_width()/2)
        scale_y = 1/(self.window_height()/2)

        scaling_matrix = Transformation.scaling_matrix(scale_x,scale_y)

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
    Normaliza e clipa pontos e linhas
    """
    def normalize_and_clip(self):
        display = []

        normalization_matrix = self.normalization_matrix()
        projection_matrix = self.orthogonal_projection_matrix()

        for obj in self.objects:

            display_coords = None
                #clipping

            if(obj.obj_type == ObjType.POINT):
                display_coords = obj.project(projection_matrix, normalization_matrix)
            elif(obj.obj_type == ObjType.WIREFRAME):
                display_coords = obj.project(projection_matrix, normalization_matrix, self.line_clipping)

            if(display_coords != None):
                display_coords = [self.viewport_transformation(point[0],point[1]) for point in display_coords]
                display_object = DisplayObject(display_coords, obj.color, obj.filled)
                display.append(display_object)

        self.display = display
