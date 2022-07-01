from model.graphic_element import GraphicElement
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType
import numpy as np
from model.wireframe_3d import Wireframe3D
from model.curve_object import CurveObject
from model.point_3d import Point3D

BEZIER_MATRIX = np.array((
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  3,  0, 0],
            [ 1,  0,  0, 0]))


class BicubicSurface(Wireframe3D):
    def __init__(self, obj_type=None, coords=[], shape=(0,0,0), color="black", filled=False):
        super().__init__(vertices=coords, edges=None, color=color, filled=filled)
        self.shape = shape
        self.obj_type = obj_type


    def patch_points(delta, control_matrix):
        curves = list()

        n = int(1/delta)

        T = list()
        for j in range(n+1):
            t = j*delta
            T.append(np.array((t*t*t, t*t, t, 1)))

        S = list()
        for i in range(n+1):
            s = i*delta
            S.append(np.array((s*s*s, s*s, s, 1)))


        num_rows, num_cols = np.shape(control_matrix)
        p = np.array([[None]*int(num_cols/3)*(n+1)]*int(num_rows/3)*(n+1))

        for row in range(0, num_rows-2, 3):
            for col in range(0, num_cols-2, 3):

                G = control_matrix[row:row+4,col:col+4]
                Gx = [[p[0] for p in l] for l in  G]
                Gy = [[p[1] for p in l] for l in  G]
                Gz = [[p[2] for p in l] for l in  G]

                for i in range(n+1):
                    for j in range(n+1):
                        x_si_tj = S[i] @ BEZIER_MATRIX @ Gx @ BEZIER_MATRIX.T @ T[j] 
                        y_si_tj = S[i] @ BEZIER_MATRIX @ Gy @ BEZIER_MATRIX.T @ T[j] 
                        z_si_tj = S[i] @ BEZIER_MATRIX @ Gz @ BEZIER_MATRIX.T @ T[j]
                        point = Point3D((x_si_tj, y_si_tj, z_si_tj))

                        p[((int(row/3))*(n+1))+i][((int(col/3))*(n+1))+j] = point

        return p

    
    def wireframe_list(self, d):
        wireframes = list()
        control_matrix = np.reshape(self.vertices, (self.shape[0], self.shape[1], 3))
        points_matrix = BicubicSurface.patch_points(d,control_matrix)
        (rows, cols) = np.shape(points_matrix)
        edges = [(0,1),(1,2),(2,3),(3,0)]
        for i in range(rows-1):
            for j in range(cols-1):
                square = Wireframe3D([points_matrix[i][j],points_matrix[i][j+1],points_matrix[i+1][j+1],points_matrix[i+1][j]], edges, self.color, self.filled)
                wireframes.append(square)
        return wireframes


    def project(self, projection_matrix, line_clipping, d, viewport_transformation_matrix):
        control_matrix = np.reshape(self.vertices, (self.shape[0], self.shape[1]))
        display_objects = list()
        edges = [(0,1),(1,2),(2,3),(3,0)]

        if(self.obj_type == ObjType.BEZIER_SURFACE):
            points_matrix = BicubicSurface.patch_points(d,control_matrix)

            (rows, cols) = np.shape(points_matrix)
            for i in range(rows-1):
                for j in range(cols-1):
                    square = [points_matrix[i][j],points_matrix[i][j+1],points_matrix[i+1][j+1],points_matrix[i+1][j]]
                    
                    display_object =  super().project(projection_matrix, line_clipping, square, edges, viewport_transformation_matrix)
                    if(display_object != None):
                        display_objects += display_object
            
        if(len(display_objects)>0):
            return display_objects
        return None