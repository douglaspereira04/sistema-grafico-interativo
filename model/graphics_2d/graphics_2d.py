import math
import numpy as np
from model.obj_type import ObjType
from model.graphics_2d.graphic_2d_element import Graphic2DElement
from model.graphics_2d.point_2d import Point2D
from model.graphics_2d.transformation_2d import Transformation2D
from model.clipper import LineClipping
from enum import Enum

class Axis(Enum):
    X = 1
    Y = 2

class Graphics2D:
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
            "x_max": 0., 
            "x_min": 0.,
            "y_max": 0., 
            "y_min": 0.
        }
        self.window = {
            "width": 0.,
            "height": 0.
        }

        self.border = 20.0
        self.line_clipping = LineClipping.LIAN_BARSK
        self.enable_clipping = True
        self.default_window = None

        self.center = Point2D((0,0))
        self.vup = Point2D((0,1))
        self.vrv = Point2D((1,0))


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
        return self.center.coords

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
        (center,dimension, vpn, vup) = window
        (width,height, depth) = dimension

        self.set_window_width(width,aspect)

        if(self.window_height() < height):
            self.set_window_height(height,aspect)

        self.default_window = window
        self.center.set_coords(center)

    def get_window(self):
        return (self.window_center(),(self.window_width(),self.window_height(),0), None, None)


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
        if(axis == Axis.X):
            axis = self.vrv.coords
        elif(axis == Axis.Y):
            axis = self.vup.coords

        translation_matrix = Transformation2D.translation_matrix(axis[0]*steps, axis[1]*steps)

        self.center.transform(translation_matrix)

    def rotate(self, rad):
        
        transformation_matrix = Transformation2D.rotation_matrix(rad, None)
            
        self.vup.transform(transformation_matrix)
        self.vrv.transform(transformation_matrix)

    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, object_index, transformation_list):
        self.objects[object_index].transform_from_list(transformation_list)

    def get_vup_angle(self):
        (x,y,_) = self.vup.coords
        vup_angle =  math.atan2(x, y)

        return vup_angle

    def normalization_matrix(self):

        (x,y,_) = self.center.coords
        translation_matrix = Transformation2D.translation_matrix(-x,-y)

        vup_angle = self.get_vup_angle()

        rotation_matrix = Transformation2D.rotation_matrix(vup_angle, None)
        scaling_matrix = Transformation2D.scaling_matrix(2/self.window_width(),2/self.window_height())

        return translation_matrix @ rotation_matrix @ scaling_matrix


    """
    Transformação para viewport
     - Ajustado para a representação em sistema de coordenadas normalizado
     - Ajustado para clippling
    """

    def viewport_transformation_matrix(self):
        w = self.viewport_width()
        h = self.viewport_height()
        b = self.border
        c1 = (w - (b*2)) / 2
        c2 = (h - (b*2)) / 2

        return np.array([[c1,0.,0.],[0.,-c2,0.],[c1+b,c2+b,1.]])

