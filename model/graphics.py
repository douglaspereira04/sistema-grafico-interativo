import math
import numpy as np
from model.obj_type import ObjType
from model.graphic_object import GraphicObject
from model.display_object import DisplayObject
from model.transformation import Transformation
from model.clipper import LineClipping

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

        normalization_matrix = self.normalization_matrix()

        for obj in self.objects:
            scn_clipped_coords = None

            obj.normalize(normalization_matrix)

            display_object = None
            if(self.enable_clipping == True):
                #clipping

                if(obj.obj_type == ObjType.POINT):
                    scn_clipped_coords = obj.clip()
                elif(obj.obj_type == ObjType.LINE):
                    scn_clipped_coords = obj.clip(self.line_clipping)
                elif(obj.obj_type == ObjType.WIREFRAME):
                    scn_clipped_coords = obj.clip()
                elif(obj.obj_type == ObjType.BEZIER):
                    scn_clipped_coords = obj.clip(int(self.viewport_width()/10))
                elif(obj.obj_type == ObjType.SPLINE):
                    scn_clipped_coords = obj.clip(self.window_width()*0.1/self.viewport_width())

                
                if(scn_clipped_coords != None):
                    display_object = DisplayObject(scn_clipped_coords, obj.color, obj.filled)


            else:
                #caso o clipping esteja desativado
                display_object = DisplayObject(obj.scn, obj.color, obj.filled)

            if(display_object != None):
                display_object.coords = [self.viewport_transformation(point[0],point[1]) for point in display_object.coords]
                display.append(display_object)

        self.display = display
