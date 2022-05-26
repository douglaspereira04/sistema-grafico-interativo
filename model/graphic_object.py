class GraphicObject:
    def __init__(self, name=None, obj_type=None,coords=[], color="black", filled=False):
        self.name = name
        self.obj_type = obj_type
        self.coords = coords
        self.color = color
        self.filled = filled

    def centroid(self):

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
