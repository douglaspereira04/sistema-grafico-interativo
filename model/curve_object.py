from model.graphic_object import GraphicObject
from model.obj_type import ObjType
import numpy as np

BEZIER_MATRIX = [
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  3,  0, 0],
            [ 1,  0,  0, 0]]

class CurveObject(GraphicObject):
    def __init__(self, name=None, coords=[], color="black", filled=False):
        super().__init__(name, ObjType.BEZIER, coords, color, filled)

    
    def bezier_point(t, control_points):
        t = [t*t*t, t*t, t, 1]
        bezier_matrix = BEZIER_MATRIX

        control_x = [point[0] for point in control_points]
        control_y = [point[1] for point in control_points]

        t_bezier = np.matmul(t, bezier_matrix)

        x =  np.matmul(t_bezier, control_x)
        y = np.matmul(t_bezier, control_y)


        return (x,y)

    def blended_points(self, resolution):
        control_points = self.coords
        curve_points = []
        width = resolution
        length = len(control_points)
        for i in range(0, length-1, 3):
            curr_control_points = control_points[i:i+4]
            for j in range(width):
                curve_points.append(CurveObject.bezier_point(j/width, curr_control_points))

        return curve_points