# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Lab4 TextureMapping
   Description :
   Author :       zdf's desktop
   date：          2019/2/24
-------------------------------------------------
   Change Activity:
                   2019/2/24:23:27
-------------------------------------------------
"""
import math
import numpy as np
import random

from PIL import Image
from pyglet.gl import *


class Edge:

    def __init__(self, v1, v2):
        # v1, v2 for two vertices of that edge
        self.ymax = 0
        self.ymin = 0
        self.xmin = 0
        self.slope = 0
        self.v1 = v1
        self.v2 = v2


class ScreenVertex:

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Pixel:

    def __init__(self, cord=None, normal=None, color=(0.5, 0.5, 0.5)):
        if normal is None:
            normal = [0, 0, 0]
        if cord is None:
            cord = [0, 0]
        self.cord = cord
        self.normal = normal
        self.color = color


class Vertex:

    def __init__(self, cord=None, color=(0.5, 0.5, 0.5), normal=None):
        if cord is None:
            cord = [0, 0, 0]
        if normal is None:
            normal = []
        self.cord = cord
        self.normal = normal
        self.color = color


class Polygon:

    def __init__(self):
        self.vertex_num = 0
        self.vertex_list = []
        self.main_color = (255, 255, 255)
        self.edge_table = []
        self.pixel_list = []  # all pixels inside this polygon(including vertex)
        self.normal = np.zeros(3, dtype=np.float64) # the normal vector of polygon

    def print(self):
        """
        Print attributes of polygon
        :return: None
        """
        print("Vertex Number:", self.vertex_num)
        for i, v in enumerate(self.vertex_list):
            print("Vertex", i, ":", v)
        print(self.main_color)
        print(self.edge_table)
        print(self.pixel_list)
        print(self.normal)


class Model:
    """
    Model contains data of vertices and polygons
    """

    def __init__(self):
        self.raw_vertex = []
        self.raw_polygon = []
        self.final_vertex = []  # ScreenVertex
        self.final_polygon = []  # viewing polygon under current observer after backface-culling
        self.texture = []

    def load_model(self, path):
        """
        load raw data from file to a model
        :param path: the data path
        :return: None
        """
        with open(path) as f:
            read_data = f.read()
        data = read_data.replace("\t", " ").replace("data", "").split("\n")
        try:
            data.remove("")
        except Exception:
            pass

        temp = data[0].split(" ")
        temp = [x for x in temp if x]  # filter the duplicated empty element.
        point_number = temp[0]

        data = data[1:]  # trim the first data

        for i, val in enumerate(data):
            if i < int(point_number):
                self.raw_vertex.append(val.split(" "))
            else:
                self.raw_polygon.append(val.split(" "))

        for i, v in enumerate(self.raw_vertex):
            temp = [float(x) for x in v if x]
            temp.append(1)
            v = Vertex(temp, [], (0, 0, 0))
            self.raw_vertex[i] = v

        for i, p in enumerate(self.raw_polygon):
            temp = [int(x) for x in p if x]
            self.raw_polygon[i] = temp

    def find_pologon_normal(self):
        """
        Find the normal vector of polygon
        :return:
        """
        for p in self.final_polygon:
            p.normal = np.zeros(3, dtype=np.float64)
            v1 = self.raw_vertex[p.vertex_list[0]].cord
            v2 = self.raw_vertex[p.vertex_list[1]].cord
            v3 = self.raw_vertex[p.vertex_list[2]].cord
            # print(v1, v2, v3)
            v1 = v1[:-1]
            v2 = v2[:-1]
            v3 = v3[:-1]
            e1 = np.subtract(v2, v1)
            e2 = np.subtract(v3, v2)
            p.normal = np.cross(e1, e2)
            p.normal /= np.linalg.norm(p.normal)
            # print("p.normal = ", p.normal)

    def find_vertex_normal(self):
        """
        Find the normal vector of vertex
        :return:
        """
        for i, v in enumerate(self.raw_vertex):
            temp_normal = [0, 0, 0]
            for p in self.final_polygon:
                if i in p.vertex_list:
                    temp_normal += p.normal
            if np.linalg.norm(temp_normal):
                temp_normal /= np.linalg.norm(temp_normal)
            # print("Vertex Normal:", temp_normal)
            v.normal = temp_normal
            # v.color = illumination_model(v.normal)
        print("finishing vertex normal calculation")

    def zoom_model(self, amplifier, shift):
        '''
        Zoom and shift model to the center of the screen
        :param amplifier: Zoom multiple
        :param shift: Shift multiple
        :return:
        '''
        for v in self.final_vertex:
            v.x = v.x * amplifier + shift
            v.y = v.y * amplifier + shift

    def create_edge_table(self):
        """
        Creating an edge_table for a certain model
        :return: None
        """
        for p in self.final_polygon:
            num = p.vertex_num  # vertices number of this polygon
            for i in range(0, num):
                '''
                Warning: 
                to Visit proper vertex, you need to 
                add -1 on index since the vertex are labeled start by 1, not 0.
                '''
                index1 = p.vertex_list[i]
                if i == num - 1:
                    index2 = p.vertex_list[0]
                else:
                    index2 = p.vertex_list[i + 1]

                v1 = self.final_vertex[index1]
                v2 = self.final_vertex[index2]
                if int(v1.y) == int(v2.y):
                    # skip the horizontal edge
                    continue
                e = Edge(self.raw_vertex[index1], self.raw_vertex[index2])
                e.ymax = int(max(v1.y, v2.y))  # compare Y value of V1 and V2
                e.ymin = int(min(v1.y, v2.y))
                e.xmin = v1.x if v1.y < v2.y else v2.x  # store the x value of the bottom vertex
                e.slope = (v1.x - v2.x) / (v1.y - v2.y)  # store the edge slope for coherence

                e.ymax -= 1  # dealing with vertex-scanline intersection(shorten edges)

                p.edge_table.append(e)

            def ymin_cmp(edge):
                return edge.ymin

            p.edge_table.sort(key=ymin_cmp)  # sort edge_table by Y value
        print("Finished edge_table creation")

    def scan_conversion(self):
        """
        making a scan conversion on a certain model
        :return: None
        """
        print("Start Scan conversion...")
        for p in self.final_polygon:
            AET = []  # Active edge table
            if not p.edge_table:  # ignoring empty edge_table
                continue
            ymin = int(p.edge_table[0].ymin)  # ymin value among all edges
            ymax = int(max(node.ymax for node in p.edge_table))  # ymax value among all edges

            for scanY in range(ymin, ymax + 1):  # scanline Y value
                for e in p.edge_table:
                    if e.ymin == scanY:  # put edge into AET which intersect with current scanline
                        AET.append(e)
                    elif e.ymin > scanY:  # already finished since ET are pre-sorted
                        break

                def x_cmp(edge):
                    return edge.xmin

                AET.sort(key=x_cmp)  # re-sort AET by X value
                for i in range(0, len(AET) // 2, 2):
                    n1 = list(AET[i].v1.normal)
                    n2 = list(AET[i].v2.normal)
                    n3 = list(AET[i + 1].v2.normal)
                    na = [0, 0, 0]
                    nb = [0, 0, 0]
                    for v in range(3):
                        temp = AET[i].ymax - AET[i].ymin
                        # dealing with horizontal edge and using coherence
                        if temp == 0:
                            temp = 1
                        na[v] = n1[v] * (scanY - AET[i].ymin) / temp \
                         + n2[v] * (AET[i].ymax - scanY) / temp
                    for v in range(3):
                        temp = AET[i + 1].ymax - AET[i + 1].ymin
                        if temp == 0:
                            temp = 1
                        nb[v] = n1[v] * (scanY - AET[i + 1].ymin) / temp \
                         + n3[v] * (AET[i + 1].ymax - scanY) / temp
                    for j in range(int(AET[i].xmin), int(AET[i + 1].xmin)):
                        # for each intersections between scanline and edge
                        # store all pixels coordinate between them into a pixel list
                        Np = [0, 0, 0]
                        for v in range(3):
                            Np[v] = na[v] * (int(AET[i + 1].xmin) - j) / (int(AET[i + 1].xmin) - int(AET[i].xmin)) \
                             + nb[v] * (j - int(AET[i].xmin)) / (int(AET[i + 1].xmin) - int(AET[i].xmin))
                        color = illumination_model(self.texture, Np)
                        # using illumination model to texture map and calculate light intensity
                        cord = [j, scanY]
                        pixel = Pixel(cord, color=color)
                        p.pixel_list.append(pixel)

                for e in AET:
                    if e.ymax == scanY:  # remove edges that no longer intersect with the next scanline
                        AET.remove(e)
                for e in AET:
                    e.xmin += e.slope  # adjust X value by coherence
                AET.sort(key=x_cmp)  # re-sort AET by X value
        print("Finished Scanline conversion")


class Observer:
    """
    Observer provide certain parameters to observe specific model.
    """

    def __init__(self):
        self.local = []
        self.camera = []
        self.up_vector = []
        self.p_ref = []
        self.near = 0
        self.far = 0
        self.width = 0
        self.u = []
        self.v = []
        self.n = []

        self.model_matrix = np.identity(4, dtype=np.float64)
        self.view_matrix = np.zeros(4, dtype=np.float64)
        self.pers_matrix = np.zeros(4, dtype=np.float64)
        self.final_matrix = np.zeros(4, dtype=np.float64)

    def set_modeling_matrix(self, l):
        self.local = l

    def set_viewing_matrix(self, c, up):
        self.camera = c
        self.up_vector = up

    def set_perspective_matrix(self, n, f, h):
        self.near = n
        self.far = f
        self.width = h

    def set_project_ref(self, p):
        self.p_ref = p

    def calculate_uvn(self):
        self.n = np.zeros(3, dtype=np.float64)
        self.n = np.subtract(self.n, self.camera)  # Warning! this is n - camera(Pref - c), not the backwards!
        self.n /= np.linalg.norm(self.n)  # calculate the magnitude of vector N

        self.u = np.zeros(3, dtype=np.float64)
        temp = np.cross(self.n, self.up_vector)  # calculate the N x V'
        temp /= np.linalg.norm(temp)  # divided by |N x V'|
        self.u = temp

        self.v = np.cross(self.n, self.u)

    def calculate_matrix(self):
        temp = np.identity(4, dtype=np.float64)

        temp[0][3] = self.local[0]
        temp[1][3] = self.local[1]
        temp[2][3] = self.local[2]
        self.model_matrix = temp

        temp = np.identity(4, dtype=np.float64)  # calculate T matrix, save as temp
        for i in range(0, 3):
            temp[i][3] = -self.camera[i]
        T = temp

        temp = np.identity(4, dtype=np.float64)  # calculate R matrix, save as temp
        # print(type(n))
        temp[0][0] = self.u[0]
        temp[0][1] = self.u[1]
        temp[0][2] = self.u[2]
        temp[1][0] = self.v[0]
        temp[1][1] = self.v[1]
        temp[1][2] = self.v[2]
        temp[2][0] = self.n[0]
        temp[2][1] = self.n[1]
        temp[2][2] = self.n[2]

        R = temp
        self.view_matrix = R @ T

        temp = np.zeros((4, 4), dtype=np.float64)
        temp[0][0] = self.near / self.width
        temp[1][1] = self.near / self.width
        temp[2][2] = self.far / (self.far - self.near)
        temp[2][3] = - (self.far * self.near / (self.far - self.near))
        temp[3][2] = 1

        self.pers_matrix = temp
        self.final_matrix = self.pers_matrix @ self.view_matrix


def texture_mapping(width, height, normal):
    """
    Compute texture mapping coordinate using sphere mapping
    :param width: total pixel width
    :param height: total pixel height
    :param normal: pixel normal vector
    :return: index of mapping position
    """
    r = width / (2 * math.pi)
    theta = math.acos(normal[0]) * 180 / math.pi
    u = (theta / 180) * width
    v = (normal[1] + 1) * height / 2
    return [u, v]


def load_texture(filename):
    """
    Load the texture file
    :param filename: Texture file name
    :return: image object in numpy array format
    """
    im = np.array(Image.open(filename))
    # print(im.shape, im.dtype, im.size, type(im))
    width = im.shape[0]
    height = im.shape[1]
    # print(width, height)
    return im


def illumination_model(im, normal):
    """
    Calculating light intensity and texture mapping
    :param im: image object in numpy array format
    :param normal: pixel normal
    :return:
    """
    diffuse, specular, ambient = [0, 0, 0], [0, 0, 0], [0, 0, 0]
    light_intensity = [0.0, 0.0, 0.0]
    light_source = [0.4, 0.8, 0.9]  # color of light

    h_vector = np.zeros(3, dtype=np.float64)
    light_direction = np.zeros(3, dtype=np.float64)
    light_direction = [0.8, -0.8, 0.5]

    view_direction = np.zeros(3, dtype=np.float64)
    h_vector = light_direction + view_direction
    h_vector /= np.linalg.norm(h_vector)

    kd = 0.2  # diffuse term
    ks = 0.4  # specular term
    ka = 0.3  # ambient term

    temp = texture_mapping(im.shape[0], im.shape[1], normal)
    u = temp[0] - 1
    v = temp[1] - 1
    # prevent overflow

    for i in range(0, 3):
        diffuse[i] = kd * light_source[i] * np.dot(normal, light_direction)
        specular[i] = ks * light_source[i] * np.dot(normal, h_vector)
        ambient[i] = ka * light_source[i]
        light_intensity[i] = diffuse[i] + specular[i] + ambient[i] + im[int(v)][int(u)][i] / 255
        # applying texture color
    return tuple(light_intensity)


def calculate_vertex(model, observer):
    """
    calculate final vertex of a model under a certain observe parameter
    :param model:
    :param observer:
    :return:
    """
    model.final_vertex.insert(0, ScreenVertex(0, 0))
    model.raw_vertex.insert(0, Vertex())
    # add a void vertex at leftmost to make sure vertex index start from 1
    for i, v in enumerate(model.raw_vertex):
        if i == 0:
            continue
        v = observer.pers_matrix @ observer.view_matrix @ v.cord
        v[0] = v[0] / v[3]
        v[1] = v[1] / v[3]
        vertex = ScreenVertex(v[0], v[1])
        model.final_vertex.append(vertex)


def backface_culling(model, observer):
    """
    Applying back-face culling on certain model under a certain observe parameter
    :param model:
    :param observer:
    :return:
    """
    view_vertex = []  # vertex temp-list in view space
    for i, v in enumerate(model.raw_vertex):
        if i == 0:
            continue
        v = observer.pers_matrix @ observer.view_matrix @ v.cord  # vertex in view space
        view_vertex.append(v)

    for p in model.raw_polygon:
        v1 = np.subtract(view_vertex[p[2] - 1], view_vertex[p[1] - 1])
        v2 = np.subtract(view_vertex[p[3] - 1], view_vertex[p[2] - 1])

        v1 = v1[:-1]
        v2 = v2[:-1]
        Pn = np.cross(v1, v2)

        if Pn[2] > 0:
            temp = Polygon()
            temp.vertex_num = p[0]
            for v in range(1, temp.vertex_num + 1):
                temp.vertex_list.append(p[v])
            model.final_polygon.append(temp)


def fill_polygon(model_list):
    """
    for all model in model_list, draw the model
    :param model_list: processed model
    :return: None
    """
    window = pyglet.window.Window(1920, 1080, resizable=True)
    @window.event
    def on_draw():
        print("Start drawing...")
        window.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        main_batch = pyglet.graphics.Batch()
        for i in model_list:
            for p in i.final_polygon:
                for pixel in p.pixel_list:
                    main_batch.add(1, gl.GL_POINTS, None,
                                   ('v2f', (pixel.cord[0], pixel.cord[1])),
                                   ('c3d', pixel.color)
                                   )
        main_batch.draw()
        print("Finish drawing...")


if __name__ == "__main__":
    model_list = []
    m1 = Model()
    # m1.load_model('./knight.d.txt')
    m1.load_model('./queen.d.txt')
    texture = load_texture('Floor.bmp')
    # texture = load_texture('Conc.bmp')
    m1.texture = texture

    o1 = Observer()
    o1.set_modeling_matrix([0, 0, 0])  # input local-to-world parameter
    o1.set_viewing_matrix([23, 20, -10], [-1, -1, 0])  # input camera position and up-vector parameter
    o1.set_perspective_matrix(10, 80, 10)  # input Near & far volume and width
    o1.set_project_ref([0, 0, 0])  # input project reference

    o1.calculate_uvn()
    o1.calculate_matrix()

    calculate_vertex(m1, o1)
    m1.zoom_model(3000, 450)

    backface_culling(m1, o1)

    m1.find_pologon_normal()
    m1.find_vertex_normal()

    m1.create_edge_table()
    m1.scan_conversion()

    model_list.append(m1)

    '''

    m2 = Model()
    m2.load_model('./queen.d.txt')
    calculate_vertex(m2, o1)
    m2.zoom_model(3500, 450)
    backface_culling(m2, o1)
    m2.create_edge_table()
    m2.scan_conversion()
    model_list.append(m2)

    '''

    fill_polygon(model_list)
    pyglet.app.run()
