from model.obj_type import ObjType
from model.graphic_element import GraphicElement
from model.graphic_object import GraphicObject
from model.point_3d import Point3D
from model.wireframe_3d import Wireframe3D
from model.curve_object import CurveObject
import re
import numpy as np

class WavefrontObj:
    def parse(graphics, mtlib_name):
        object_list = graphics.objects

        window_center = tuple(graphics.window_center())
        window_size = tuple((graphics.window_width(), graphics.window_height(), graphics.window_depth()))
        vpn = tuple(graphics.vpn.coords)
        vup = tuple(graphics.vup.coords)

        string_file = ""

        vertex_to_pos = dict()
        objects = dict()
        obj_to_color = dict()
        color_to_mtlib = dict()

        wavefront_object_list = []


        vertex_count = 1

        color_count = 1


        vertex_to_pos[window_center] = vertex_count
        vertex_to_pos[window_size] = vertex_count+1
        vertex_to_pos[vpn] = vertex_count+2
        vertex_to_pos[vup] = vertex_count+3
        vertex_count += 4

        for obj in object_list:
            obj_string = None

            _type = None
            if(len(obj.elements)==1):
                obj_string = "\no "+obj.name
            else:
                obj_string = "\ng "+obj.name

            elements = obj.elements.copy()
            i = 0
            d = 1/10
            while(i < len(elements)):
                element = elements[i]
                if((element.obj_type == ObjType.BEZIER_SURFACE) or (element.obj_type == ObjType.SPLINE_SURFACE)):
                    elements += element.wireframe_list(d)
                    i+=1
                    continue

                if(not (element.color in color_to_mtlib.keys())):
                    color_to_mtlib[element.color] = "color_" + str(color_count)
                    color_count +=1

                obj_string += "\nusemtl " +color_to_mtlib[element.color]

                if(element.obj_type == ObjType.POINT):
                    _type = "\np"
                elif(element.obj_type == ObjType.LINE):
                    _type = "\nl"
                else:
                    if(element.filled):
                        _type = "\nf"
                    else:
                        _type = "\nl"

                obj_string += _type

                obj_coords = None

                if(element.obj_type == ObjType.POINT):
                    obj_coords = [element.coords]
                elif(element.obj_type == ObjType.BEZIER):
                    obj_coords = CurveObject.blended_points(d, element.vertices)
                elif(element.obj_type == ObjType.SPLINE):
                    obj_coords = CurveObject.forward_difference_points(d, element.vertices)
                else:
                    obj_coords = element.vertices

                _len = len(obj_coords)
                for j in range(_len):
                    if(not (tuple(obj_coords[j]) in vertex_to_pos.keys())):
                        vertex_to_pos[tuple(obj_coords[j])] = vertex_count
                        vertex_count += 1

                    vertex_pos = vertex_to_pos[tuple(obj_coords[j])]

                    obj_string += " "+ str(vertex_pos)

                i+=1

            wavefront_object_list.append(obj_string)


        vertices = []
        for vertex in vertex_to_pos.keys():
            p = vertex
            vertices.append("v "+ f"{p[0]:.6f}" +" "+ f"{p[1]:.6f}" +" "+ f"{p[2]:.6f}" + "\n")


        mtlib_inf = []
        mtlib_inf.append("mtllib "+mtlib_name+"\n")

        window_inf = ["o window\nw 1 2 3 4\n"]
        obj_file = vertices + mtlib_inf + window_inf +wavefront_object_list

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
            if(line.startswith("mtllib ")):
                mtlib_list.append(line.split(" ")[1])
        return mtlib_list

    def compose(obj,mtlib_map):

        objects = []
        ungrouped = GraphicObject(name="ungrouped")
        element_to_vertices = dict()
        element_to_object = dict()
        curr_mtl_to_hex = None
        curr_obj = None
        window_inf = None
        vertices = []
        curr_name = None
        curr_color = "#000000"
        curr_type = None

        for line in obj.splitlines():
            line = list(filter(None, re.split(r'\s|\t', line)))

            if(len(line)>0):
                if(line[0] == "v"):
                    vertex = (float(line[1]),float(line[2]),float(line[3]))
                    vertices.append(vertex)
                    last_vertex = len(vertices)-1

                elif(line[0] == "mtllib"):
                    curr_mtl_to_hex = WavefrontObj.get_mtl_to_hex(mtlib_map,line[1])

                elif(line[0] == "o" or line[0] == "g"):
                    if(curr_obj != None):
                        if(len(curr_obj.elements) == 0):
                            if(curr_obj in  objects):
                                objects.remove(curr_obj)

                    curr_name = ""
                    if(len(line)>1):
                        curr_name = line[1]
                    curr_type = line[0]
                    curr_obj = GraphicObject(name=curr_name)
                    objects.append(curr_obj)

                elif(line[0] == "usemtl"):
                    if(len(line) == 1):
                        curr_color = "#F0F0F0"
                    else:
                        material = line[1].split(".")[0]
                        curr_color = curr_mtl_to_hex[material]


                elif(line[0] == "p" or line[0] == "l" or line[0] == "f"):
                    obj_vertices = (last_vertex, [int(vertex.split("/")[0]) for vertex in line[1:]])
                    length = len(obj_vertices[1])
                    last_vertex = len(vertices)-1
                    if(line[0] == "p"):
                        element = Point3D(color=curr_color)
                    elif(line[0] == "l"):
                        element = Wireframe3D(color=curr_color, filled=False)
                    elif(line[0] == "f"):
                        element = Wireframe3D(color=curr_color, filled=True)

                    element_to_vertices[element] = obj_vertices
                    
                    if(curr_obj is None):
                        ungrouped.elements.append(element)
                    else:
                        curr_obj.elements.append(element)


                elif(line[0] == "w"):
                    objects.remove(curr_obj)
                    last_vertex = len(vertices)-1
                    window_inf = [int(line[1]),int(line[2]),int(line[3]),int(line[4]), last_vertex]



        for element in element_to_vertices.keys():
            (last_vertex, vertices_indexes) = element_to_vertices[element]
            
            for vertex in vertices_indexes:
                v = None
                if(vertex < 0):
                    v = vertices[1+last_vertex+vertex]
                elif(vertex>0):
                    v = vertices[vertex-1]

                if(element.obj_type == ObjType.WIREFRAME):
                    point = np.array([v[0],v[1],v[2],1])
                    element.vertices.append(point)
                elif(element.obj_type == ObjType.POINT):
                    element.set_coords(v)

        window = None
        if(not(window_inf is None)):
            window = []
            last_vertex = window_inf[4]
            for i in range(4):
                vertex = window_inf[i]
                if(vertex < 0):
                    window.append(vertices[1+last_vertex+vertex])
                elif(vertex>0):
                    window.append(vertices[vertex-1])
            tuple(window)

        if(len(ungrouped.elements)>0):
            objects.append(ungrouped)

        return (objects, window)


    def get_mtl_to_hex(mtlib_map, mtlib_name):
        mtl_to_hex = dict()

        mtlib = mtlib_map[mtlib_name]

        lines = mtlib.splitlines()

        i = 0
        while i < len(lines):
            line = list(filter(None, re.split(r'\s|\t', lines[i])))

            mtl = None
            
            if(len(line)>0):
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

    def get_mtl_to_hex(mtlib_map, mtlib_name):
        mtl_to_hex = dict()

        mtlib = mtlib_map[mtlib_name]

        lines = mtlib.splitlines()

        i = 0
        while i < len(lines):
            line = list(filter(None, re.split(r'\s|\t', lines[i])))

            mtl = None
            
            if(len(line)>0):
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