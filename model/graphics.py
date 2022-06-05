import math
import numpy as np
from model.obj_type import ObjType
from model.graphic_object import GraphicObject
from model.display_object import DisplayObject
from model.transformation import Transformation
from model.clipper import Clipper, LineClipping

class Graphics:
    def __init__(self):
        self.objects = []

        self.display = []

        """
        Os valores de viewport e window são inicializados com 0
        mas são atualizados pelo controller para serem compatíveis
        com o tamanho da interface. O controller ajustará inicialmente o 
        tamanho da window igual o tamanho da viewport
        """
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

        self.zoom = 1
        self.vup_angle = 0
        self.border = 20
        self.line_clipping = LineClipping.LIAN_BARSK
        self.enable_clipping = True
        self.default_window = None

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


    def window_center(self):
        x = (self.window["x_max"] + self.window["x_min"] )/2
        y = (self.window["y_max"] + self.window["y_min"] )/2

        return (x,y)

    def set_window_height(self, height, center, aspect):
        (x,y) = center
        half_height = (height/2)
        self.window["y_min"] = y - half_height
        self.window["y_max"] = y + half_height

        half_width = (height*aspect)/2

        self.window["x_min"] = x - half_width
        self.window["x_max"] = x + half_width

    def set_window_width(self, width, center, aspect):

        (x,y) = center
        half_width = (width/2)
        self.window["x_min"] = x - half_width
        self.window["x_max"] = x + half_width

        half_height = (width/aspect)/2
        self.window["y_min"] = y - half_height
        self.window["y_max"] = y + half_height


    def reset_window(self):
        self.set_window(self.default_window)
    """
    Define o tamanho da window, mantendo a proporção da window anterior
    """
    def set_window(self,window):
        aspect = self.window_aspect_ratio()
        (center,dimension) = window
        (x,y) = center
        (width,height) = dimension

        self.set_window_width(width,center,aspect)

        if(self.window_height() < height):
            self.set_window_height(height,center,aspect)

        self.default_window = window

    def get_window(self):
        return (self.window_center(),(self.window_width(),self.window_height()))

    """
    A seguir são as funções que de navegação. Elas se orientam a um valor de passo, definido no parametro "step".
    A função zoom_in diminui a window, limitando a um tamanho maior que zero e zoom_out aumenta a window.
    As funções de panning movem a window considerando o angulo em que ela está rotacionada, 
    ou seja, o angulo de view up vector 
    """
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
        _sin = (math.sin(math.radians(self.vup_angle)))
        _cos = (math.cos(math.radians(self.vup_angle)))

        self.window["x_max"] += _cos*step
        self.window["x_min"] += _cos*step
        self.window["y_max"] -= _sin*step
        self.window["y_min"] -= _sin*step


    def pan_left(self, step):
        _sin = (math.sin(math.radians(self.vup_angle)))
        _cos = (math.cos(math.radians(self.vup_angle)))

        self.window["x_max"] -= _cos*step
        self.window["x_min"] -= _cos*step
        self.window["y_max"] += _sin*step
        self.window["y_min"] += _sin*step

    def pan_up(self, step):
        _sin = (math.sin(math.radians(self.vup_angle)))
        _cos = (math.cos(math.radians(self.vup_angle)))

        self.window["x_max"] += _sin*step
        self.window["x_min"] += _sin*step
        self.window["y_max"] += _cos*step
        self.window["y_min"] += _cos*step

    def pan_down(self, step):
        _sin = (math.sin(math.radians(self.vup_angle)))
        _cos = (math.cos(math.radians(self.vup_angle)))

        self.window["x_max"] -= _sin*step
        self.window["x_min"] -= _sin*step
        self.window["y_max"] -= _cos*step
        self.window["y_min"] -= _cos*step

    """
    Transforma, por uma dada lista de transformações, um dado objeto
    """
    def transform_from_list(self, object_index, transformation_list):
        self.objects[object_index].transform_from_list(transformation_list)
        

    """
    Retorna a matriz de normalização para as configurações 
    atuais da window
    """
    def normalization_matrix(self):
        (x_center, y_center) = self.window_center()
        translation_matrix = Transformation.translation_matrix(-x_center,-y_center)

        rotation_matrix = Transformation.rotation_matrix(-self.vup_angle)

        scale_x = 1/(self.window_width()/2)
        scale_y = 1/(self.window_height()/2)

        scaling_matrix = Transformation.scaling_matrix(scale_x,scale_y)

        normalization_matrix = np.matmul(np.matmul(translation_matrix,rotation_matrix),scaling_matrix)
        return  normalization_matrix


    """
    Transformação para viewport
     - Ajustado para a representação em sistema de coordenadas normalizado
     - Ajustado para clippling
    """
    def viewport_transformation(self, x, y):
        x1 = ((x- -1) * (self.viewport_width() - (self.border*2)) / 2) + self.border
        y1 = ((1 - ((y - -1) / 2)) * (self.viewport_height() - (self.border*2))) + self.border
        return (x1,y1)



    """
    Normaliza e clipa pontos e linhas
    """
    def normalize_and_clip(self):
        display = []
        objects_temp = self.objects.copy()

        normalization_matrix = self.normalization_matrix()
        for obj in objects_temp:
            scn_coords = []
            scn_clipped_coords = None
            obj_coords = None
            is_line_set = False
            if(obj.obj_type == ObjType.BEZIER):
                obj_coords = self.blended_points(obj.coords)
                is_line_set = True
            else:
                obj_coords = obj.coords

            for coords in obj_coords:
                #normalização
                new_coords = Transformation.transform_point(coords,normalization_matrix)
                scn_coords.append(new_coords)

            display_object = None
            if(self.enable_clipping == True):
                #clipping

                if(obj.obj_type == ObjType.POINT):
                    scn_clipped_coords = Clipper.point_clipping(scn_coords)

                    if(scn_clipped_coords != None):
                        display_object = DisplayObject(scn_clipped_coords, obj.color, False)
                elif(obj.obj_type == ObjType.LINE):
                    if(self.line_clipping == LineClipping.LIAN_BARSK):
                        scn_clipped_coords = Clipper.lian_barsk_clipping(scn_coords)
                    else:
                        scn_clipped_coords = Clipper.cohen_sutherland_clipping(scn_coords)

                    if(scn_clipped_coords != None):
                        display_object = DisplayObject(scn_clipped_coords, obj.color, False)
                elif(obj.obj_type == ObjType.WIREFRAME or obj.obj_type == ObjType.BEZIER):
                    if(not obj.filled):
                        scn_clipped_coords = Clipper.line_set_clipping(scn_coords, self.line_clipping)
                    else:
                        scn_clipped_coords = Clipper.sutherland_hodgman_clipping(scn_coords)


                    if(scn_clipped_coords != None):
                        display_object = DisplayObject(scn_clipped_coords, obj.color, obj.filled)


            else:
                #caso o clipping esteja desativado
                display_object = DisplayObject(scn_coords, obj.color, obj.filled)

            if(display_object != None):
                display_object.coords = [self.viewport_transformation(point[0],point[1]) for point in display_object.coords]
                display.append(display_object)

        self.display = display

    def bezier_matrix(self):
        return [
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  3,  0, 0],
            [ 1,  0,  0, 0]]

    def bezier_point(self, t, control_points):
        t = [t*t*t, t*t, t, 1]
        bezier_matrix = self.bezier_matrix()

        control_x = [point[0] for point in control_points]
        control_y = [point[1] for point in control_points]

        t_bezier = np.matmul(t, bezier_matrix)

        x =  np.matmul(t_bezier, control_x)
        y = np.matmul(t_bezier, control_y)


        return (x,y)

    def blended_points(self, control_points):
        curve_points = []
        width = int(self.viewport_width()*self.zoom/4)
        length = len(control_points)
        for i in range(0, length-1, 3):
            curr_control_points = control_points[i:i+4]
            for j in range(width):
                curve_points.append(self.bezier_point(j/width, curr_control_points))

        return curve_points