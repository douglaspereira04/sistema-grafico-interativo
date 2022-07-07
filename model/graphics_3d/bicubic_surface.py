from model.graphics_3d.graphic_3d_element import Graphic3DElement
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType
import numpy as np
from model.graphics_3d.wireframe_3d import Wireframe3D
from model.graphics_3d.curve_3d import Curve3D
from model.graphics_3d.point_3d import Point3D
from model.graphics_3d.transformation_3d import Transformation3D

BEZIER_MATRIX = np.array((
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  3,  0, 0],
            [ 1,  0,  0, 0]))

BEZIER_MATRIX_T = np.array((
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  3,  0, 0],
            [ 1,  0,  0, 0]))


B_SPLINE_MATRIX = np.array((
            [-1/6,  1/2, -1/2, 1/6],
            [ 1/2, -1,    1/2, 0],
            [-1/2,  0,    1/2, 0],
            [ 1/6,  2/3,  1/6, 0]))


B_SPLINE_MATRIX_T = np.transpose(np.array((
            [-1/6,  1/2, -1/2, 1/6],
            [ 1/2, -1,    1/2, 0],
            [-1/2,  0,    1/2, 0],
            [ 1/6,  2/3,  1/6, 0])))


def E(delta):
    return np.array(([0,             0,            0,     1],
            [ delta**3,     delta**2,     delta, 0],
            [ 6*(delta**3), 2*(delta**2), 0,     0],
            [6*(delta**3),  0,            0,     0]
            ))


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


    def create_forward_difference_matrix(s, t, Gx, Gy, Gz, delta_s, delta_t):

        Cx = B_SPLINE_MATRIX @ Gx @ B_SPLINE_MATRIX_T
        Cy = B_SPLINE_MATRIX @ Gy @ B_SPLINE_MATRIX_T
        Cz = B_SPLINE_MATRIX @ Gz @ B_SPLINE_MATRIX_T

        Mbs = B_SPLINE_MATRIX
        E_delta_s =  E(delta_s)
        E_delta_t_T =  E(delta_t).T

        DDx = E_delta_s @ Cx @ E_delta_t_T
        DDy = E_delta_s @ Cy @ E_delta_t_T
        DDz = E_delta_s @ Cz @ E_delta_t_T
        
        return [DDx, DDy, DDz]

    def update_forward_difference_matrixes(DDx, DDy, DDz):
        DDx[0] += DDx[1]
        DDx[1] += DDx[2]
        DDx[2] += DDx[3]

        DDy[0] += DDy[1]
        DDy[1] += DDy[2]
        DDy[2] += DDy[3]

        DDz[0] += DDz[1]
        DDz[1] += DDz[2]
        DDz[2] += DDz[3]


    def update_forward_difference(Dx, Dy, Dz):
        Dx[0][0] += Dx[0][1]
        Dx[0][1] += Dx[0][2]
        Dx[0][2] += Dx[0][3]

        Dy[0][0] += Dy[0][1]
        Dy[0][1] += Dy[0][2]
        Dy[0][2] += Dy[0][3]

        Dz[0][0] += Dz[0][1]
        Dz[0][1] += Dz[0][2]
        Dz[0][2] += Dz[0][3]

    def forward_difference_surface(DDx, DDy,DDz,n_s,n_t):

        p = np.array([[None]*n_t]*n_s)

        for i in range(0,n_s):
            curve = list()
        
            curr_DDx = DDx.copy()
            curr_DDy = DDy.copy()
            curr_DDz = DDz.copy()

            for j in range(0,n_t):
                p[i][j] = np.array([curr_DDx[0][0],curr_DDy[0][0],curr_DDz[0][0],1.0])
                BicubicSurface.update_forward_difference(curr_DDx, curr_DDy, curr_DDz)
            
            BicubicSurface.update_forward_difference_matrixes(DDx, DDy, DDz)
            
        return p

    def spline_surface_points(delta_s, delta_t, control_points):

        n_t = int(1/delta_t)
        n_s = int(1/delta_s)

        num_rows, num_cols, _ = np.shape(control_points)

        patch_points = None
        points = np.empty(((num_rows-3)*n_s, (num_cols-3)*n_t), dtype=object)

        for row in range(num_rows-3):
            for col in range(num_cols-3):

                Gx = control_points[row:row+4,col:col+4,0]
                Gy = control_points[row:row+4,col:col+4,1]
                Gz = control_points[row:row+4,col:col+4,2]

                
                (DDx,DDy,DDz) = BicubicSurface.create_forward_difference_matrix(delta_s,delta_t,Gx,Gy,Gz,delta_s,delta_t)
                patch_points = BicubicSurface.forward_difference_surface(DDx, DDy,DDz,n_s,n_t)


                for i in range(n_s):
                    for j in range(n_t):
                        points[(row*n_s)+i][(col*n_t)+j] = patch_points[i][j]


        return points




    def bezier_surface_points(delta_s, delta_t, control_matrix):
        curves = list()

        n_s = int(1/delta_s)
        n_t = int(1/delta_t)

        T = list()
        for j in range(n_t+1):
            t = j*delta_t
            T.append(np.array((t*t*t, t*t, t, 1)))

        S = list()
        for i in range(n_s+1):
            s = i*delta_s
            S.append(np.array((s*s*s, s*s, s, 1)))


        num_rows, num_cols, _ = np.shape(control_matrix)
        p = np.array([[None]*int(num_cols/3)*(n_t+1)]*int(num_rows/3)*(n_s+1))

        for row in range(0, num_rows-2, 3):
            for col in range(0, num_cols-2, 3):

                Gx = control_matrix[row:row+4,col:col+4, 0]
                Gy = control_matrix[row:row+4,col:col+4, 1]
                Gz = control_matrix[row:row+4,col:col+4, 2]

                for i in range(n_s+1):
                    for j in range(n_t+1):
                        x_si_tj = S[i] @ BEZIER_MATRIX @ Gx @ BEZIER_MATRIX_T @ T[j] 
                        y_si_tj = S[i] @ BEZIER_MATRIX @ Gy @ BEZIER_MATRIX_T @ T[j] 
                        z_si_tj = S[i] @ BEZIER_MATRIX @ Gz @ BEZIER_MATRIX_T @ T[j]
                        point = np.array([x_si_tj, y_si_tj, z_si_tj,1])

                        p[((int(row/3))*(n_s+1))+i][((int(col/3))*(n_t+1))+j] = point

        return p

    
    def wireframe_list(self, d):
        wireframes = list()
        control_matrix = np.reshape(self.vertices, (self.shape[0], self.shape[1], 4))

        points_matrix = None
        if(self.obj_type == ObjType.BEZIER_SURFACE):
            points_matrix = BicubicSurface.bezier_surface_points(d,d,control_matrix)
        if(self.obj_type == ObjType.SPLINE_SURFACE):
            points_matrix = BicubicSurface.spline_surface_points(d,d,control_matrix)

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

        points_matrix = None

        if(self.obj_type == ObjType.BEZIER_SURFACE):
            points_matrix = BicubicSurface.bezier_surface_points(d,d,control_matrix)
        if(self.obj_type == ObjType.SPLINE_SURFACE):
            points_matrix = BicubicSurface.spline_surface_points(d,d,control_matrix)

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
                        v = np.array([projected[k][0], projected[k][1],1.])
                        projected[k] =  Transformation3D.transform_point(v, viewport_transformation_matrix)
                    
                    self.projected.append(projected)