import math
import numpy as np
from model.obj_type import ObjType
from model.graphic_element import GraphicElement
from model.display_object import DisplayObject
from model.point_3d import Point3D
from model.transformation_3d import Transformation3D
from model.transformation import Transformation, RotationType, Rotation, Translation
from model.clipper import LineClipping
from enum import Enum
from PyQt5 import QtGui
from PyQt5.QtCore import QPoint

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
            "height": 0,
            "depth": 20
        }

        self.border = 20
        self.line_clipping = LineClipping.LIAN_BARSK
        self.enable_clipping = True
        self.default_window = None

        self.vrp = Point3D(np.array([0,0,0,1]))
        self.vpn = Point3D(np.array([0,0,1,1]))
        self.vup = Point3D(np.array([0,1,0,1]))

        self.cop_d = 100


    def window_width(self):
        return self.window["width"]

    def window_height(self):
        return self.window["height"]

    def window_depth(self):
        return self.window["depth"]

    def viewport_width(self):
        return self.viewport["x_max"] - self.viewport["x_min"]

    def viewport_height(self):
        return self.viewport["y_max"] - self.viewport["y_min"]

    def window_aspect_ratio(self):
        return self.window["width"]/self.window["height"]

    def viewport_aspect_ratio(self):
        return self.window_width()/self.window_height()


    def window_center(self):
        return self.vrp.coords

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
        self.vpn = Point3D(vpn)
        self.vup = Point3D(vup)

        self.window["depth"] = depth
        self.set_window_width(width,aspect)

        if(self.window_height() < height):
            self.set_window_height(height,aspect)

        self.default_window = window
        self.vrp.set_coords(center)

    def get_window(self):
        return (self.window_center(),(self.window_width(),self.window_height(),self.window_depth()), self.vpn.get_coords(), self.vup.get_coords())


    def get_angles(self):
        x_angle = 0
        vpn = self.vpn.coords
        vup = self.vup.coords
        unit_vpn = Transformation3D.unit_vector(vpn)
        if (unit_vpn != None):
            (x,y,z,_) = vpn
            x_angle = math.atan2(y, z)
            vpn = Transformation3D.transform_point(vpn, Transformation3D.rotation_x_matrix(x_angle))
            vup = Transformation3D.transform_point(vup, Transformation3D.rotation_x_matrix(x_angle))

        
        (x,y,z,_) = vpn
        y_angle = - math.atan2(x, z)
        vpn = Transformation3D.transform_point(vpn, Transformation3D.rotation_y_matrix(y_angle))
        vup = Transformation3D.transform_point(vup, Transformation3D.rotation_y_matrix(y_angle))

        (x,y,z,_) = vup
        z_angle = math.atan2(x, y)
        vpn = Transformation3D.transform_point(vpn, Transformation3D.rotation_z_matrix(z_angle))
        vup = Transformation3D.transform_point(vup, Transformation3D.rotation_z_matrix(z_angle))

        return (x_angle, y_angle, z_angle)


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
            axis = np.cross(self.vpn.coords[:3], self.vup.coords[:3])
        elif(axis == Axis.Y):
            axis = self.vup.coords
        else:
            axis = self.vpn.coords

        translation_matrix = Transformation3D.translation_matrix(axis[0]*steps, axis[1]*steps, axis[2]*steps)

        self.vrp.transform(translation_matrix)

    def rotate(self, axis, rad):
        
        if(axis == Axis.X):
            axis = np.cross(self.vpn.coords[:3], self.vup.coords[:3])
            transformation_matrix = Transformation3D.rotation_given_axis_matrix(rad, axis, None)
        elif(axis == Axis.Y):
            axis = self.vup.coords
            transformation_matrix = Transformation3D.rotation_given_axis_matrix(rad, axis, None)
        else:
            axis = self.vpn.coords
            transformation_matrix = Transformation3D.rotation_given_axis_matrix(rad, axis, None)
            
        self.vup.transform(transformation_matrix)
        self.vpn.transform(transformation_matrix)


    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, object_index, transformation_list):
        self.objects[object_index].transform_from_list(transformation_list)
        

    def projection_normalization_matrix(self):

        (x,y,z,_) = self.vrp.coords
        translation_matrix = Transformation3D.translation_matrix(-x,-y,-z)

        (x_angle, y_angle, z_angle) = self.get_angles()
        rotation_x = Transformation3D.rotation_x_matrix(x_angle)
        rotation_y = Transformation3D.rotation_y_matrix(y_angle)
        rotation_z = Transformation3D.rotation_z_matrix(z_angle)

        rotation_matrix = rotation_x @ rotation_y @ rotation_z

        scaling_matrix = Transformation3D.scaling_matrix(2/self.window_width(),2/self.window_height(), 2/self.window_depth())
        
        d_factor = self.cop_d*(2/self.window_depth())
        perspective_matrix = np.array(np.transpose([
                [1.,0.,0.,0.], 
                [0.,1.,0.,0.], 
                [0.,0.,1.,0],
                [0.,0.,1.0/d_factor,1.]
            ]))

        return translation_matrix @ rotation_matrix @ scaling_matrix @ perspective_matrix




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

        return np.array([[c1,0,0],[0,-c2,0],[c1+b,c2+b,1]])


    """
    Normaliza e clipa pontos e linhas
    """
    def normalize_and_clip(self, painter, color):
        display = list()

        if(color != None):
            painter.setPen(color)
            painter.setBrush(QtGui.QBrush(color))
            for obj in self.objects:
                for element in obj.elements:
                    self.draw_projected_element(element, color, painter)

        else:
            projection_normalization_matrix = self.projection_normalization_matrix()
            viewport_transformation_matrix = self.viewport_transformation_matrix()
            d = self.window_width()/(10*self.viewport_width())
            
            for obj in self.objects:
                for element in obj.elements:
                    element.project(None, projection_normalization_matrix, self.line_clipping, d,viewport_transformation_matrix)
                    color = QtGui.QColor(element.color)
                    self.draw_projected_element(element, color, painter)

    def draw_projected_element(self,element, color, painter):
        projected = element.projected
        painter.setPen(color)
        painter.setBrush(QtGui.QBrush(color))

        if(element.obj_type == ObjType.POINT):
            if(not (projected is None)):
                painter.drawPoint(projected[0], projected[1])

        elif((element.obj_type == ObjType.WIREFRAME or element.obj_type == ObjType.BEZIER or element.obj_type == ObjType.SPLINE) and (not element.filled)):
            if(len(projected) > 0):
                for line in element.projected:
                    painter.drawLine(line[0][0],line[0][1],line[1][0],line[1][1])

        elif((element.obj_type == ObjType.BEZIER or element.obj_type == ObjType.SPLINE or element.obj_type == ObjType.WIREFRAME) and element.filled):
            if(not (projected is None)):
                vertices = [QPoint(p[0], p[1]) for p in element.projected]
                polygon = QtGui.QPolygon(vertices)
                painter.drawPolygon(polygon)

        elif(element.obj_type == ObjType.BEZIER_SURFACE):
            if(element.filled):
                for square in element.projected:
                    vertices = [QPoint(p[0], p[1]) for p in square]
                    polygon = QtGui.QPolygon(vertices)
                    painter.drawPolygon(polygon)
            else:
                for square in element.projected:
                    for i in range(1,len(square)):
                        painter.drawLine(square[i-1][0],square[i-1][1],square[i][0],square[i][1])
                    painter.drawLine(square[0][0],square[0][1],square[-1][0],square[-1][1])
