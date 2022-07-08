from model.graphics_2d.graphic_2d_element import Graphic2DElement
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType
import numpy as np
from model.graphics_2d.wireframe_2d import Wireframe2D
from model.graphics_2d.point_2d import Point2D

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

class Curve2D(Wireframe2D):
    def __init__(self, obj_type=None, coords=[], color="black", filled=False):
        super().__init__(vertices=coords, color=color, filled=filled)
        self.obj_type = obj_type

    def bezier_point(t, control_points):
        T = np.array((t*t*t, t*t, t, 1))

        Gx = np.array([p[0] for p in control_points])
        Gy = np.array([p[1] for p in control_points])


        x =  T @ BEZIER_MATRIX @ Gx
        y = T @ BEZIER_MATRIX @ Gy


        return np.array([x,y,1])

    def blended_points(d, control_points):
        curve_points = []
        n = int(1/d)
        length = len(control_points)
        for i in range(0, length-1, 3):
            curr_control_points = control_points[i:i+4]
            for j in range(n):
                curve_points.append(Curve2D.bezier_point(j/n, curr_control_points))


        return curve_points

    def create_forward_difference_matrix(control_points, delta):
        Gx = np.array(np.transpose([[p[0] for p in control_points]]))
        Gy = np.array(np.transpose([[p[1] for p in control_points]]))

        Mbs = B_SPLINE_MATRIX
        E_delta =  E(delta)

        Dx = E_delta @ Mbs @ Gx
        Dy = E_delta @ Mbs @ Gy
        
        return [Dx, Dy]

    def update_forward_difference(Dx, Dy):
        Dx[0][0] += Dx[1][0]
        Dx[1][0] += Dx[2][0]
        Dx[2][0] += Dx[3][0]

        Dy[0][0] += Dy[1][0]
        Dy[1][0] += Dy[2][0]
        Dy[2][0] += Dy[3][0]

    def forward_difference(delta, Dx, Dy):
        points = []

        n = int(1/delta)

        for i in range(1,n):

            Curve2D.update_forward_difference(Dx, Dy)
            points.append(np.array([Dx[0][0],Dy[0][0],1]))

        return points

    def forward_difference_points(delta, control_points):
        curve_points = []
        length = len(control_points)
        i = 0
        while i+3 < length:
            curr_control_points = control_points[i:i+4]
            [Dx, Dy] = Curve2D.create_forward_difference_matrix(curr_control_points,delta)
            curve_points += Curve2D.forward_difference(delta, Dx, Dy)
            i+=1

        return curve_points


    
    def normalize(self, vertices = None, normalization_matrix = None, line_clipping = None, d = None, viewport_transformation_matrix = None):
        if(self.obj_type == ObjType.BEZIER):
            vertices = Curve2D.blended_points(d, self.vertices)
        else:
            vertices = Curve2D.forward_difference_points(d, self.vertices)

        super().project(vertices, normalization_matrix, line_clipping, d, viewport_transformation_matrix)