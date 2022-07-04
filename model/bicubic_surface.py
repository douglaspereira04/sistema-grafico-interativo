from model.graphic_element import GraphicElement
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType
import numpy as np
from model.wireframe_3d import Wireframe3D
from model.curve_object import CurveObject
from model.point_3d import Point3D
from model.transformation_3d import Transformation3D

BEZIER_MATRIX = np.array((
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  3,  0, 0],
            [ 1,  0,  0, 0]))


class BicubicSurface(Wireframe3D):
    def __init__(self, obj_type=None, coords=[], shape=(0,0,0), color="black", filled=False):
        super().__init__(vertices=coords, color=color, filled=filled)
        self.shape = shape
        self.obj_type = obj_type


    def __str__(self):
        string = ""
        line_size = self.shape[1]
        i = 0
        for v in self.vertices:
            if(i == line_size):
                i = 0
                string = string[:-1]
                string += ";"
            string += str(tuple(v[:-1]))+","
            i+=1

        return string[:-1]


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


        num_rows, num_cols, _ = np.shape(control_matrix)
        p = np.array([[None]*int(num_cols/3)*(n+1)]*int(num_rows/3)*(n+1))

        for row in range(0, num_rows-2, 3):
            for col in range(0, num_cols-2, 3):

                Gx = control_matrix[row:row+4,col:col+4, 0]
                Gy = control_matrix[row:row+4,col:col+4, 1]
                Gz = control_matrix[row:row+4,col:col+4, 2]

                for i in range(n+1):
                    for j in range(n+1):
                        x_si_tj = S[i] @ BEZIER_MATRIX @ Gx @ BEZIER_MATRIX.T @ T[j] 
                        y_si_tj = S[i] @ BEZIER_MATRIX @ Gy @ BEZIER_MATRIX.T @ T[j] 
                        z_si_tj = S[i] @ BEZIER_MATRIX @ Gz @ BEZIER_MATRIX.T @ T[j]
                        point = np.array([x_si_tj, y_si_tj, z_si_tj,1])

                        p[((int(row/3))*(n+1))+i][((int(col/3))*(n+1))+j] = point

        return p

    
    def wireframe_list(self, d):
        wireframes = list()
        control_matrix = np.reshape(self.vertices, (self.shape[0], self.shape[1], 4))

        if(self.obj_type == ObjType.BEZIER_SURFACE):
            points_matrix = BicubicSurface.patch_points(d,control_matrix)
            (rows, cols) = np.shape(points_matrix)
            for i in range(rows-1):
                for j in range(cols-1):
                    square = Wireframe3D([points_matrix[i][j],points_matrix[i][j+1],points_matrix[i+1][j+1],points_matrix[i+1][j]], self.color, self.filled)
                    wireframes.append(square)
            return wireframes

        return None


    def project(self, vertices = None, projection_matrix = None, line_clipping = None, d = None, viewport_transformation_matrix = None):
        control_matrix = np.reshape(self.vertices, (self.shape[0], self.shape[1], 4))
        self.projected = list()

        if(self.obj_type == ObjType.BEZIER_SURFACE):
            points_matrix = BicubicSurface.patch_points(d,control_matrix)

            (rows, cols) = np.shape(points_matrix)
            for i in range(rows-1):
                for j in range(cols-1):
                    square = [points_matrix[i][j],points_matrix[i][j+1],points_matrix[i+1][j+1],points_matrix[i+1][j]]
                    projected_vertices = [None] * 4

                    for k in range(4):
                        [x,y,z,w] = Transformation3D.transform_point(square[k], projection_matrix)
                        projected_vertices[k] = [x/w, y/w]

                    projected = Clipper.sutherland_hodgman_clipping(projected_vertices)
                    if(not(projected is None)):
                        for k in range(len(projected)):
                            v = np.array([projected[k][0], projected[k][1],1])
                            projected[k] =  v @ viewport_transformation_matrix
                        
                        self.projected.append(projected)