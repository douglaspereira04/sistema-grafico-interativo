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
        x1 = int((x- self.window["x_min"]) * self.viewport_width() / self.window_width())
        y1 = int((1 - ((y - self.window["y_min"]) / self.window_height())) * self.viewport_height())
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