class GraphicObject:
    def __init__(self, name=None, obj_type=None,coords=[], color="black"):
        self.name = name
        self.obj_type = obj_type
        self.coords = coords
        self.color = color

        self.scn_coords = []

    def centroid(self):
        x_coords = [point[0] for point in self.coords]
        y_coords = [point[1] for point in self.coords]
        _len = len(self.coords)
        centroid_x = sum(x_coords)/_len
        centroid_y = sum(y_coords)/_len
        return (centroid_x, centroid_y)
