import math
import numpy as np
from enum import Enum

class RotationType(Enum):
    OBJECT_CENTER = 1
    WORLD_CENTER = 2
    GIVEN_POINT = 3

class TransformationType(Enum):
    TRANSLATION = 1
    SCALING = 2
    ROTATION = 3


class Graphics:
    def __init__(self):
        self.objects = []
        self.viewport = {
            "x_max": 0, 
            "x_min": 0,
            "y_max": 0, 
            "y_min": 0
        }
        self.window = {
            "x_max": 0, 
            "x_min": 0,
            "y_max": 0, 
            "y_min": 0
        }

    def viewport_transformation(self, x, y):
        x1 = ((x- self.window["x_min"]) * self.viewport_width() / self.window_width())
        y1 = ((1 - ((y - self.window["y_min"]) / self.window_height())) * self.viewport_height())
        return (x1,y1)

    def window_width(self):
        return self.window["x_max"] - self.window["x_min"]

    def window_height(self):
        return self.window["y_max"] - self.window["y_min"]

    def viewport_width(self):
        return self.viewport["x_max"] - self.viewport["x_min"]

    def viewport_height(self):
        return self.viewport["y_max"] - self.viewport["y_min"]

    def window_aspect_ratio(self):
        return self.window_width()/self.window_height()

    def viewport_aspect_ratio(self):
        return self.window_width()/self.window_height()

    def zoom_in(self, step):
        aspect = self.window_aspect_ratio()

        xmax = self.window["x_max"] - ((step/2)*aspect)
        ymax = self.window["y_max"] - (step/2)
        xmin = self.window["x_min"] + ((step/2)*aspect)
        ymin = self.window["y_min"] + (step/2)

        if (((xmax - xmin )<= 0) or ((ymax - ymin) <= 0)):

            return False
        else:
            self.window["x_max"] = xmax
            self.window["y_max"] = ymax
            self.window["x_min"] = xmin
            self.window["y_min"] = ymin
            
            return True


    def zoom_out(self, step):
        aspect = self.window_aspect_ratio()

        self.window["x_max"] += (step/2)*aspect
        self.window["y_max"] += (step/2)
        self.window["x_min"] -= (step/2)*aspect
        self.window["y_min"] -= (step/2)


    def pan_right(self, step):
        self.window["x_max"] += step
        self.window["x_min"] += step


    def pan_left(self, step):
        self.window["x_max"] -= step
        self.window["x_min"] -= step

    def pan_up(self, step):
        self.window["y_max"] += step
        self.window["y_min"] += step

    def pan_down(self, step):
        self.window["y_max"] -= step
        self.window["y_min"] -= step

    def translation(self, x, y):
        return (TransformationType.TRANSLATION, (x, y))

    def scale(self, scale):
        return (TransformationType.SCALING, scale)

    def natural_rotation(self, degrees, centroid):
        (x,y) = centroid
        return (TransformationType.ROTATION, (RotationType.OBJECT_CENTER, degrees, x, y))

    def translation_matrix(self, x, y):
        return [[1.0,  0.,  0.],[ 0,  1.0,  0.],[ x,  y,  1.]]

    def scaling_matrix(self, x, y):
        return [[x,  0.,  0.],[ 0,  y,  0.],[ 0., 0., 1.]]

    def rotation_matrix(self, degrees):
        _sin = (math.sin(math.radians(degrees)))
        _cos = (math.cos(math.radians(degrees)))

        return [[ _cos,  -_sin,  0.],[ _sin,  _cos,  0.],[ 0.,  0.,  1.]]


    def transform_from_list(self, object_index, transformation_list):

        coords = self.objects[object_index].coords
        centroid = self.objects[object_index].centroid()

        transformation_matrix = self.get_transformation_matrix_composition(transformation_list,centroid)
        
        if(len(transformation_matrix)>0):
            for i in range(len(coords)):
                coords[i] = self.transform(coords[i], transformation_matrix)


    def get_transformation_matrix_composition(self, transformation_list,centroid):
        
        transformation_matrixes = [self.get_transformation_matrix(transformation,centroid) for transformation in transformation_list]
        transformation_matrix_composition = []
        if(len(transformation_matrixes) > 0):
            transformation_matrix_composition = transformation_matrixes[0]

            for i in range(len(transformation_matrixes)-1):
                transformation_matrix_composition = np.matmul(transformation_matrix_composition,transformation_matrixes[i+1])

        return transformation_matrix_composition

    def get_transformation_matrix(self, transformation,centroid):

        #SCALING (OBJ CENTER)
        if (transformation[0] == TransformationType.SCALING):
            parcial = np.matmul(self.translation_matrix(-centroid[0], -centroid[1]),self.scaling_matrix(transformation[1],transformation[1]))
            return np.matmul(parcial,self.translation_matrix(centroid[0], centroid[1]))
        #ROTATION
        if (transformation[0] == TransformationType.ROTATION):
            #WORLD
            if(transformation[1][0] == RotationType.WORLD_CENTER):
                return self.rotation_matrix(transformation[1][1])
            #OBJECT
            if (transformation[1][0] == RotationType.OBJECT_CENTER):
                parcial = np.matmul(self.translation_matrix(-centroid[0], -centroid[1]),self.rotation_matrix(transformation[1][1]))
                return np.matmul(parcial,self.translation_matrix(centroid[0], centroid[1]))
            #POINT
            if (transformation[1][0] == RotationType.GIVEN_POINT):
                parcial = np.matmul(self.translation_matrix(-transformation[1][2], -transformation[1][3]),self.rotation_matrix(transformation[1][1]))
                return np.matmul(parcial, self.translation_matrix(transformation[1][2], transformation[1][3]))
        #TRANSLATION
        if (transformation[0] == TransformationType.TRANSLATION):
            return self.translation_matrix(transformation[1][0],transformation[1][1])

    def transform(self, point, transformation_matrix):
        (x,y) = point
        [x1,y1,z1] = np.matmul([x,y,1],transformation_matrix)
        return (x1,y1)
        
