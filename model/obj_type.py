from enum import Enum

class ObjType(Enum):
    POINT = 1
    LINE = 2
    WIREFRAME = 3
    BEZIER = 4
    SPLINE = 5
    BEZIER_SURFACE = 6
    SPLINE_SURFACE = 7