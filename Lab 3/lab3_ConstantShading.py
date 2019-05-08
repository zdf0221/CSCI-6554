# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     lab3_Shadings
   Description :
   Author :       zdf's desktop
   date：          2019/2/24
-------------------------------------------------
   Change Activity:
                   2019/2/24:23:27
-------------------------------------------------
"""

import numpy as np
import random
from pyglet.gl import *


class Edge:

    def __init__(self):
        self.ymax = 0
        self.ymin = 0
        self.xmin = 0
        self.slope = 0


class ScreenVertex:

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Pixel:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Vertex:

    def __init__(self, cord, normal=None):
        if normal is None:
            normal = []
        self.cord = cord
        self.normal = normal


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
        # self.visible_vertex = []  # viewing vertices under current observer after backface-culling

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
            v = Vertex(temp, [])
            self.raw_vertex[i] = v

        for i, p in enumerate(self.raw_polygon):
            temp = [int(x) for x in p if x]
            self.raw_polygon[i] = temp

    def find_pologon_normal(self):
        for p in self.final_polygon:
            p.normal = np.zeros(3, dtype=np.float64)
            v1 = self.raw_vertex[p.vertex_list[0] - 1].cord
            v2 = self.raw_vertex[p.vertex_list[1] - 1].cord
            v3 = self.raw_vertex[p.vertex_list[2] - 1].cord
            print(v1, v2, v3)
            v1 = v1[:-1]
            v2 = v2[:-1]
            v3 = v3[:-1]
            e1 = np.subtract(v2, v1)
            e2 = np.subtract(v3, v2)
            p.normal = np.cross(e1, e2)
            p.normal /= np.linalg.norm(p.normal)
            print("p.normal = ", p.normal)

    def zoom_model(self, amplifier, shift):
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
                v1 = self.final_vertex[p.vertex_list[i]]
                if i == num - 1:
                    v2 = self.final_vertex[p.vertex_list[0]]
                else:
                    v2 = self.final_vertex[p.vertex_list[i + 1]]
                if int(v1.y) == int(v2.y):
                    # skip the horizontal edge
                    continue
                e = Edge()
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
                for i in range(len(AET) // 2):
                    for j in range(int(AET[i].xmin), int(AET[i + 1].xmin)):
                        # for each intersections between scanline and edge
                        # store all pixels coordinate between them into a pixel list
                        pixel = Pixel(j, scanY, 0)
                        p.pixel_list.append(pixel)

                for e in AET:
                    if e.ymax == scanY:  # remove edges that no longer intersect with the next scanline
                        AET.remove(e)
                for e in AET:
                    e.xmin += e.slope  # adjust X value by coherence
                AET.sort(key=x_cmp)  # re-sort AET by X value
        print("Finished Scanline conversion")

    def illumination_model(self):
        diffuse, specular, ambient = [0, 0, 0], [0, 0, 0], [0, 0, 0]
        light_intensity = [0.0, 0.0, 0.0]
        light_source = [0.5, 1.0, 0.8]  # color of light
        # light_source[0] = 0.5
        h_vector = np.zeros(3, dtype=np.float64)
        light_direction = np.zeros(3, dtype=np.float64)
        light_direction[0] = 1.5
        print("LightDir = ", light_direction)

        view_direction = np.zeros(3, dtype=np.float64)
        h_vector = light_direction + view_direction
        h_vector /= np.linalg.norm(h_vector)
        print("h_vector = ", h_vector)

        kd = 0.3  # diffuse term
        ks = 0.6  # specular term
        ka = 0.2  # ambient term
        for p in self.final_polygon:
            for i in range(0, 3):
                diffuse[i] = kd * light_source[i] * np.dot(p.normal, light_direction)
                specular[i] = ks * light_source[i] * np.dot(p.normal, h_vector)
                ambient[i] = ka * light_source[i]
                light_intensity[i] = diffuse[i] + specular[i] + ambient[i]
            print(tuple(light_intensity))
            p.main_color = tuple(light_intensity)


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


def calculate_vertex(model, observer):
    """
    calculate final vertex of a model under a certain observe parameter
    :param model:
    :param observer:
    :return:
    """
    model.final_vertex.append(ScreenVertex(0, 0))  # add a void vertex to make sure vertex index start from 1
    for i, v in enumerate(model.raw_vertex):
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

    # vertex_list = pyglet.graphics.vertex_list(0)

    @window.event
    def on_draw():
        print("Start drawing...")
        window.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        main_batch = pyglet.graphics.Batch()
        for i in model_list:
            for p in i.final_polygon:
                color = p.main_color
                print("Current color:", color)
                for pixel in p.pixel_list:
                    main_batch.add(1, gl.GL_POINTS, None,
                                   ('v2f', (pixel.x, pixel.y)),
                                   ('c3d', color)
                                   )
        main_batch.draw()
        print("Finish drawing...")


if __name__ == "__main__":
    model_list = []
    m1 = Model()
    # m1.load_model('./donut.d.txt')
    # m1.load_model('./car.d.txt')
    # m1.load_model('./knight.d.txt')
    m1.load_model('./queen.d.txt')
    # m1.load_model('./cow.d.txt')

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

    m1.create_edge_table()
    m1.scan_conversion()
    m1.find_pologon_normal()
    m1.illumination_model()
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
