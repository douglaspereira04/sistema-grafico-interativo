class Graphics:
    def __init__(self):
        self.objects = []
        self.viewport = {
            "x_max": 300, 
            "x_min": 0,
            "y_max": 300, 
            "y_min": 0
        }
        self.window = {
            "x_max": 300, 
            "x_min": 0,
            "y_max": 300, 
            "y_min": 0
        }

    def viewport_transformation(self, x, y):
        x1 = int((x- self.window["x_min"]) * (self.viewport["x_max"] - self.viewport["x_min"]) / (self.window["x_max"] - self.window["x_min"]))
        y1 = int((1 - ((y - self.window["y_min"]) / (self.window["y_max"] - self.window["y_min"]))) * (self.viewport["y_max"] - self.viewport["y_min"]))
        return (x1,y1)