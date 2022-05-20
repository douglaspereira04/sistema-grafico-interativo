from model.obj_type import ObjType
from model.graphic_object import GraphicObject
import re

class WavefrontObj:
    def parse(graphics, mtlib_name):
        object_list = graphics.objects

        string_file = ""

        vertex_to_pos = dict()
        objects = dict()
        obj_to_color = dict()
        color_to_mtlib = dict()

        wavefront_object_list = []


        vertex_count = 1

        color_count = 1

        for obj in object_list:
            obj_string = None

            _type = None
            if(obj.obj_type == ObjType.POINT):
                _type = "p"
            elif(obj.obj_type == ObjType.LINE):
                _type = "l"
            elif(obj.obj_type == ObjType.WIREFRAME):
                if(obj.coords[0] == obj.coords[len(obj.coords)-1]):
                    _type = "f"
                else:
                    _type = "l"



            obj_string = "o "+obj.name+"\n"+ _type

            if(not (obj.color in color_to_mtlib.keys())):
                color_to_mtlib[obj.color] = "color_" + str(color_count)
                color_count +=1

            _len = len(obj.coords)
            if(_type == "f"):
                _len -=1
            for i in range(_len):
                if(not (obj.coords[i] in vertex_to_pos.keys())):
                    vertex_to_pos[obj.coords[i]] = vertex_count
                    vertex_count += 1

                vertex_pos = vertex_to_pos[obj.coords[i]]

                obj_string += " "+ str(vertex_pos)


            obj_string += "\nusemtl " +color_to_mtlib[obj.color]+"\n"
            wavefront_object_list.append(obj_string)


        vertices = []
        for vertex in vertex_to_pos.keys():
            vertices.append("v "+ f"{vertex[0]:.6f}" +" "+ f"{vertex[1]:.6f}" +" "+ f"{0:.6f}" + "\n")
        mtlib_inf = []
        mtlib_inf.append("mtlib "+mtlib_name+"\n")
        obj_file = vertices + mtlib_inf +wavefront_object_list

        mtlib_file = []
        for color in color_to_mtlib.keys():
            mtlib_string = ""
            (r,g,b) = WavefrontObj.hex_to_rgb(color)

            mtlib_string += "newmtl "+color_to_mtlib[color]+ "\n"
            mtlib_string += "Kd " + f"{r:.6f}" +" "+ f"{g:.6f}" +" "+ f"{b:.6f}" + "\n"
            mtlib_file.append(mtlib_string)

        return (obj_file, mtlib_file)


    def get_mtlib_list(obj):
        mtlib_list = []
        for line in obj.splitlines():
            if(line.startswith("mtlib ")):
                mtlib_list.append(line.split(" ")[1])
        return mtlib_list

    def compose(obj,mtlib_map):

        objects = []

        object_to_vertices = dict()
        curr_mtl_to_hex = None
        curr_object = None

        vertices = []

        for line in obj.splitlines():
            line = list(filter(None, re.split(r'\s|\t', line)))

            if(len(line)>0):
                if(line[0] == "v"):
                    vertex = (float(line[1]),float(line[2]))
                    vertices.append(vertex)

                if(line[0] == "mtlib"):
                    curr_mtl_to_hex = WavefrontObj.get_mtl_to_hex(mtlib_map,line[1])

                if(line[0] == "o"):
                    obj = GraphicObject(name=line[1])
                    curr_object = obj
                    object_to_vertices[curr_object] = None

                if(line[0] == "p" or line[0] == "l" or line[0] == "f"):
                    last_vertex = len(vertices)-1
                    object_to_vertices[curr_object] = (line[0], last_vertex, [int(vertex) for vertex in line[1:]])

                if(line[0] == "usemtl"):
                    _hex = curr_mtl_to_hex[line[1]]
                    curr_object.color = _hex


        for obj in object_to_vertices.keys():
            (_type, last_vertex, vertices_indexes) = object_to_vertices[obj]
            
            coords = []
            for vertex in vertices_indexes:
                if(vertex < 0):
                    coords.append(vertices[1+last_vertex+vertex])
                elif(vertex>0):
                    coords.append(vertices[vertex-1])

            if(_type == "p"):
                obj.obj_type = ObjType.POINT
            elif(_type == "l"):
                if(len(vertices)<3):
                    obj.obj_type = ObjType.LINE
                else:
                    obj.obj_type = ObjType.WIREFRAME
            elif(_type == "f"):
                obj.obj_type = ObjType.WIREFRAME
                coords.append(coords[0])


            obj.coords = coords

            objects.append(obj)

        return objects

    def get_mtl_to_hex(mtlib_map, mtlib_name):
        mtl_to_hex = dict()

        mtlib = mtlib_map[mtlib_name]

        lines = mtlib.splitlines()

        i = 0
        while i < len(lines):
            line = list(filter(None, re.split(r'\s|\t', lines[i])))

            mtl = None
            
            if(line[0] == "newmtl"):
                mtl = line[1]

                while line[0] != "Kd":
                    i+=1
                    line = list(filter(None, re.split(r'\s|\t', lines[i])))

                (r,g,b) = (float(line[1])*255,float(line[2])*255,float(line[3])*255)
                _hex = WavefrontObj.rgb_to_hex(r,g,b)
                mtl_to_hex[mtl] = _hex


            i+=1
        return mtl_to_hex
                



    def hex_to_rgb(value):
        value = value.lstrip('#')
        lv = len(value)
        (r,g,b) = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
        rgb = (r/255,g/255,b/255)
        return rgb


    def rgb_to_hex(r, g, b):
        return '#%02x%02x%02x' % (int(r), int(g), int(b))