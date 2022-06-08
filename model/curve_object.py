from model.graphic_object import GraphicObject
from model.clipper import Clipper, LineClipping
from model.obj_type import ObjType
import numpy as np

BEZIER_MATRIX = [
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  3,  0, 0],
            [ 1,  0,  0, 0]]

B_SPLINE_MATRIX = [
            [-1/6,  1/2, -1/2, 1/6],
            [ 1/2, -1,    1/2, 0],
            [-1/2,  0,    1/2, 0],
            [ 1/6,  2/3,  1/6, 0]]

def E(delta):
    return [[0,             0,            0,     1],
            [ delta**3,     delta**2,     delta, 0],
            [ 6*(delta**3), 2*(delta**2), 0,     0],
            [6*(delta**3),  0,            0,     0]
            ]

class CurveObject(GraphicObject):
    def __init__(self, name=None, obj_type=None, coords=[], color="black", filled=False):
        super().__init__(name, obj_type, coords, color, filled)

    
    def center(self):
        sum_x = 0
        sum_y = 0

        last_point = None

        _len = len(self.coords)
        if(self.coords[0] == self.coords[_len-1] and _len > 1):
            _len-=1

        for i in range(_len):
            sum_x += self.coords[i][0]
            sum_y += self.coords[i][1]

        centroid_x = sum_x/_len
        centroid_y = sum_y/_len
        return (centroid_x, centroid_y)

    def bezier_point(t, control_points):
        t = [t*t*t, t*t, t, 1]

        control_x = [point[0] for point in control_points]
        control_y = [point[1] for point in control_points]

        t_b = np.matmul(t, BEZIER_MATRIX)

        x =  np.matmul(t_b, control_x)
        y = np.matmul(t_b, control_y)


        return (x,y)

    def blended_points(self, resolution, control_points):
        curve_points = []
        width = resolution
        length = len(control_points)
        for i in range(0, length-1, 3):
            curr_control_points = control_points[i:i+4]
            for j in range(width):
                curve_points.append(CurveObject.bezier_point(j/width, curr_control_points))


        return curve_points

    def create_forward_difference_matrix(control_points, delta):
        Gx = np.transpose([[p[0] for p in control_points]])
        Gy = np.transpose([[p[1] for p in control_points]])

        Mbs = B_SPLINE_MATRIX
        Cx = np.matmul(Mbs, Gx)
        Cy = np.matmul(Mbs, Gy)

        E_delta =  E(delta)



        Dx = np.matmul(E_delta, Cx)
        Dy = np.matmul(E_delta, Cy)


        return (Dx, Dy)

    def update_forward_difference(Dx, Dy):
        Dx[0][0] += Dx[1][0]
        Dx[1][0] += Dx[2][0]
        Dx[2][0] += Dx[3][0]

        Dy[0][0] += Dy[1][0]
        Dy[1][0] += Dy[2][0]
        Dy[2][0] += Dy[3][0]

    def forward_difference(delta, control_points):
        line_set = []

        (Dx, Dy) = CurveObject.create_forward_difference_matrix(control_points,delta)

        n = int(1/delta)

        for i in range(1,n):

            CurveObject.update_forward_difference(Dx,Dy)
            x = Dx[0][0]
            y = Dy[0][0]

            line_set.append((x, y))
        return line_set

    def forward_difference_points(delta, control_points):
        curve_points = []
        length = len(control_points)
        i = 0
        while i+3 < length:
            curr_control_points = control_points[i:i+4]
            curve_points += CurveObject.forward_difference(delta, curr_control_points)
            i+=1


        return curve_points


    def clip(self, d):
        coords = None
        if(self.obj_type == ObjType.BEZIER):
            coords = self.blended_points(d, self.scn)
        else:
            coords = CurveObject.forward_difference_points(d, self.scn)

        if(not self.filled):
            return Clipper.line_set_clipping(coords, LineClipping.COHEN_SUTHERLAND)
        else:
            return Clipper.sutherland_hodgman_clipping(coords)
