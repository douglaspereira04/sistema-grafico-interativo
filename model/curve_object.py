from model.graphic_element import GraphicElement
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType
import numpy as np
from model.wireframe_3d import Wireframe3D
from model.point_3d import Point3D

BEZIER_MATRIX = np.array((
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  3,  0, 0],
            [ 1,  0,  0, 0]))

B_SPLINE_MATRIX = np.array((
            [-1/6,  1/2, -1/2, 1/6],
            [ 1/2, -1,    1/2, 0],
            [-1/2,  0,    1/2, 0],
            [ 1/6,  2/3,  1/6, 0]))

def E(delta):
    return np.array(([0,             0,            0,     1],
            [ delta**3,     delta**2,     delta, 0],
            [ 6*(delta**3), 2*(delta**2), 0,     0],
            [6*(delta**3),  0,            0,     0]
            ))

class CurveObject(Wireframe3D):
    def __init__(self, obj_type=None, coords=[], color="black", filled=False):
        super().__init__(vertices=coords, edges=None, color=color, filled=filled)
        self.obj_type = obj_type

    def bezier_point(t, control_points):
        T = np.array((t*t*t, t*t, t, 1))

        Gx = np.array([p.get_coords()[0] for p in control_points])
        Gy = np.array([p.get_coords()[1] for p in control_points])
        Gz = np.array([p.get_coords()[2] for p in control_points])


        x =  T @ BEZIER_MATRIX @ Gx
        y = T @ BEZIER_MATRIX @ Gy
        z = T @ BEZIER_MATRIX @ Gz


        return Point3D(coords=(x, y, z))

    def blended_points(d, control_points):
        curve_points = []
        n = int(1/d)
        length = len(control_points)
        for i in range(0, length-1, 3):
            curr_control_points = control_points[i:i+4]
            for j in range(n):
                curve_points.append(CurveObject.bezier_point(j/n, curr_control_points))


        return curve_points

    def create_forward_difference_matrix(control_points, delta):
        Gx = np.array(np.transpose([[p.get_coords()[0] for p in control_points]]))
        Gy = np.array(np.transpose([[p.get_coords()[1] for p in control_points]]))
        Gz = np.array(np.transpose([[p.get_coords()[2] for p in control_points]]))

        Mbs = B_SPLINE_MATRIX
        E_delta =  E(delta)

        Dx = E_delta @ Mbs @ Gx
        Dy = E_delta @ Mbs @ Gy
        Dz = E_delta @ Mbs @ Gz
        
        return (Dx, Dy, Dz)

    def update_forward_difference(Dx, Dy, Dz):
        Dx[0][0] += Dx[1][0]
        Dx[1][0] += Dx[2][0]
        Dx[2][0] += Dx[3][0]

        Dy[0][0] += Dy[1][0]
        Dy[1][0] += Dy[2][0]
        Dy[2][0] += Dy[3][0]

        Dz[0][0] += Dz[1][0]
        Dz[1][0] += Dz[2][0]
        Dz[2][0] += Dz[3][0]

    def forward_difference(delta, Dx, Dy, Dz):
        line_set = []

        n = int(1/delta)

        for i in range(1,n):

            CurveObject.update_forward_difference(Dx, Dy, Dz)
            x = Dx[0][0]
            y = Dy[0][0]
            z = Dz[0][0]

            line_set.append(Point3D(coords=(x, y, z)))
        return line_set

    def forward_difference_points(delta, control_points):
        curve_points = []
        length = len(control_points)
        i = 0
        while i+3 < length:
            curr_control_points = control_points[i:i+4]
            (Dx, Dy, Dz) = CurveObject.create_forward_difference_matrix(curr_control_points,delta)
            curve_points += CurveObject.forward_difference(delta, Dx, Dy, Dz)
            i+=1

        return curve_points



    def project(self, projection_matrix, line_clipping, d, viewport_transformation_matrix):
        if(self.obj_type == ObjType.BEZIER):
            vertices = CurveObject.blended_points(d, self.vertices)
        else:
            vertices = CurveObject.forward_difference_points(d, self.vertices)

        edges = [(i,i+1) for i in range(len(vertices)-1)]
        return super().project(projection_matrix, line_clipping, vertices, edges, viewport_transformation_matrix)