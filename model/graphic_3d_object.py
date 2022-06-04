import numpy as np
import numbers
from model.point_3d import Point3d
from enum import Enum

class Axis(Enum):
    X = 1
    Y = 2
    Z = 3

class Object3d:
    def __init__(self, name=None, vertices=None, edges=None, color="black", filled=False):
        self.name = name
        self.vertices = vertices
        self.edges = edges
        self.color = color
        self.filled = filled

    def centroid(self):

        sum_x = 0
        sum_y = 0
        sum_z = 0

        _len = len(self.vertices)

        for i in range(_len):
            sum_x += self.vertices[i].x
            sum_y += self.vertices[i].y
            sum_z += self.vertices[i].z

        centroid_x = sum_x/_len
        centroid_y = sum_y/_len
        centroid_z = sum_z/_len
        return Point3d(centroid_x, centroid_y,centroid_z)

    """
    Funções que criam e retornam matrizes de transformação
    dados parametros
    """
    def translation_matrix(self, x, y, z):
        return [[1.0,  0.,  0., 0.],[ 0,  1.0,  0., 0.],[ 0.,  0.,  1., 0.],[ x,  y,  z, 1.0]]

    def scaling_matrix(self, x, y, z):
        centroid = self.centroid()
        translate_center = self.transformation_matrix(-centroid.x,-centroid.y,-centroid.z)
        scale = [[x,  0.,  0., 0.],[ 0,  y,  0., 0.],[ 0., 0., z, 0.],[ 0., 0., 0., 1.0]]
        translate_original_pos = self.transformation_matrix(centroid.x,centroid.y,centroid.z)
        return np.matmul(translate_center,np.matmul(scale,translate_original_pos))

    def rotation_x_matrix(self, degrees):
        _sin = (math.sin(math.radians(degrees)))
        _cos = (math.cos(math.radians(degrees)))
        return [[ 1.0,  0.,  0., 0.], [0., _cos,  _sin,  0.],[0., -_sin,  _cos,  0.],[ 0.,  0.,  0., 1.0]]

    def rotation_y_matrix(self, degrees):
        _sin = (math.sin(math.radians(degrees)))
        _cos = (math.cos(math.radians(degrees)))
        return [[ _cos,  0.,  -_sin, 0.], [0., 1.0,  0.,  0.],[_sin, 0.,  _cos,  0.],[ 0.,  0.,  0., 1.0]]

    def rotation_z_matrix(self, degrees):
        _sin = (math.sin(math.radians(degrees)))
        _cos = (math.cos(math.radians(degrees)))
        return [[ _cos,  _sin,  0., 0.], [-_sin,  _cos, 0.,  0.],[0., 0., 1.0,  0.],[ 0.,  0.,  0., 1.0]]

    def rotation_matrix(self, axis, degrees):
        centroid = self.centroid()
        (x,y,z) = (centroid.x,centroid.y,centroid.z)
        translation = self.translation_matrix(-x,-y,-z)
        rotation_x_angle = math.atan(math.sqrt(((x)**2+(z)**2)/(y)))
        rotation_z_angle = math.atan(math.sqrt(((z)**2+(y)**2)/(x)))
        rotation_x = rotation_x_matrix(-rotation_x_angle)
        rotation_z = rotation_z_matrix(-z_angle)
        rotation_y = rotation_z_matrix(math.radians(degrees))

    def rotation_object_center_matrix(self, axis, degrees):
        rotation = None
        if(axis == Axis.X):
            rotation = self.rotation_x_matrix(degrees)
        elif(axis == Axis.Y):
            rotation = self.rotation_y_matrix(degrees)
        elif(axis == Axis.Z):
            rotation = self.rotation_z_matrix(degrees)
        else:
            return None

        centroid = self.centroid()
        (x,y,z) = (centroid.x,centroid.y,centroid.z)
        translation_center = translation_matrix(-x,-y,-z)
        translation_back = translation_matrix(x,y,z)

        return np.matmul(translate_center, np.matmul(rotation, translation_back))


    def rotation_point_matrix(self, axis, degrees, x, y ,z):
        rotation = None
        if(axis == Axis.X):
            rotation = self.rotation_x_matrix(degrees)
        elif(axis == Axis.Y):
            rotation = self.rotation_y_matrix(degrees)
        elif(axis == Axis.Z):
            rotation = self.rotation_z_matrix(degrees)
        else:
            return None

        translation_center = translation_matrix(-x,-y,-z)
        translation_back = translation_matrix(x,y,z)
        
    def rotation_matrix(self, axis, degress):
        return self.rotation_point_matrix(axis,degrees, 0,0,0)

    def rotation_object_center_matrix(self, axis, degrees):
        centroid = self.centroid()
        (x,y,z) = (centroid.x,centroid.y,centroid.z)
        return self.rotation_point_matrix(axis, degress, x,y,z)



    def transform(self, transformation_matrix):

        for i in len(self.vertices):
            vertex = self.vertices[i]
            [x,y,z,_] = np.matmul([vertex.x,vertex.y,vertex.z,1],transformation_matrix)
            self.vertices[i].x = x
            self.vertices[i].y = y
            self.vertices[i].z = z

    def from_string(name, string_vertices, string_edges, color):
        are_3d_vertices = False
        are_obj_edges = False
        vertices = None
        edges = None
        obj = None
        point_3d_list = None

        vertices = list(eval(string_vertices))
        edges = list(eval(string_edges))

        if(len(vertices) == 3 and (not isinstance(vertices[0], tuple))):
            vertices = [tuple(vertices)]


        if(len(edges) == 2 and (not isinstance(edges[0], tuple))):
            edges = [tuple(edges)]

        if(len(vertices) > 0):
            are_obj_edges = all(isinstance(e0, int) and isinstance(e1, int) and e0 < len(vertices) and e1 < len(vertices) for (e0,e1) in edges)
            are_3d_vertices = all(isinstance(x, numbers.Number) and isinstance(y, numbers.Number)  and isinstance(z, numbers.Number) for (x,y,z) in vertices)

            point_3d_list = [Point3d(x,y,z) for (x,y,z) in vertices]
            

        if(are_3d_vertices and are_obj_edges):
            obj = Object3d(name, point_3d_list,edges,color, False)

        return obj
