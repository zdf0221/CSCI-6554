# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     lab2_Scanline_Zbuffer
   Description :
   Author :       zdf's desktop
   date：          2019/2/24
-------------------------------------------------
   Change Activity:
                   2019/2/24:23:27
-------------------------------------------------
"""


import numpy as np
from pyglet.gl import *


class Model:
    '''
    Model contains data of vertices and polygons
    '''
    def __init__(self):
        self.raw_vertex = []
        self.raw_polygon = []
        self.final_vertex = []  # vertex in screen space
        self.final_polygon = []  # viewing polygon under current observer after backface-culling
        self.view_vertex = []  # viewing vertex under current observer after backface-culling
        self.edge_table = []

    def load_model(self, path):
        with open(path) as f:
            read_data = f.read()
        # print(read_data)
        # print(type(read_data))
        data = read_data.replace("\t", " ").replace("data", "").split("\n")
        try:
            data.remove("")
        except Exception:
            pass

        # print(type(data))
        # print("Raw Data: ", data)

        temp = data[0].split(" ")
        temp = [x for x in temp if x]  # filter the duplicated empty element.
        point_number = temp[0]
        polygon_number = temp[1]

        # print("Point Number:" + point_number)
        # print("Polygon Number:" + polygon_number)

        data = data[1:]  # trim the first data

        for i, val in enumerate(data):
            if i < int(point_number):
                self.raw_vertex.append(val.split(" "))
            else:
                self.raw_polygon.append(val.split(" "))

        # print("raw_vertex: ", raw_vertex)
        # print("raw_polygon: ", raw_polygon)

        for i, v in enumerate(self.raw_vertex):
            temp = [float(x) for x in v if x]
            temp.append(1)
            self.raw_vertex[i] = temp

        for i, p in enumerate(self.raw_polygon):
            temp = [int(x) for x in p if x]
            self.raw_polygon[i] = temp

        # print("raw_vertex: ", raw_vertex)
        # print("raw_polygon: ", raw_polygon)

    def zoom_model(self, amplifier, shift):
        for v in self.final_vertex:
            v[0] = v[0] * amplifier + shift
            v[1] = v[1] * amplifier + shift

    def create_edgetable(self):
        for p in self.final_polygon:
            num = p[0]  # vertices number of this polygon
            for i in range(1, num + 1):
                v1 = self.final_vertex[p[i]]
                if i == num:
                    v2 = self.final_vertex[1]
                else:
                    v2 = self.final_vertex[p[i + 1]]
                e = Edge()
                e.ymax = max(v1[1], v2[1])  # compare Y value of V1 and V2
                e.ymin = min(v1[1], v2[1])
                e.xmin = v1[0] if v1[1] < v2[1] else v2[0]  # store the x value of the bottem vertex
                e.slope = (v2[0] - v1[0]) / (v2[1] - v1[1])  # store the slope\
                print("E:", e.ymax, e.xmin, e.slope)
                self.edge_table.append(e)

            def ymin_cmp(edge):
                return edge.ymin

            self.edge_table.sort(key=ymin_cmp)
            print("Edge Table:", self.edge_table)

    def scan_conversion(self):
        AET = []  # Active edge table




class Edge:

    def __init__(self):
        self.ymax = 0
        self.ymin = 0
        self.xmin = 0
        self.slope = 0


class EdgeTable:

    def __init__(self):
        self.table = []







class Observer:
    '''
    Observer provide certain parameters to observe specific model.
    '''
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
        # print("model_matrix:", model_matrix)
        self.view_matrix = np.zeros(4, dtype=np.float64)
        # print("view_matrix:", view_matrix)
        self.pers_matrix = np.zeros(4, dtype=np.float64)
        # print("pers_matrix:", pers_matrix)
        self.final_matrix = np.zeros(4, dtype=np.float64)
        # print("final_matrix: \n", final_matrix)

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
        # print("camera:", camera)
        # print("magnitude:", np.linalg.norm(n))
        self.n /= np.linalg.norm(self.n)  # calculate the magnitude of vector N
        # print("N: ", n)

        self.u = np.zeros(3, dtype=np.float64)
        # print("up-vector:", up_vector)
        temp = np.cross(self.n, self.up_vector)  # calculate the N x V'
        # print(np.linalg.norm(temp))
        temp /= np.linalg.norm(temp)  # divided by |N x V'|
        self.u = temp
        # print("U: ", u)

        self.v = np.cross(self.n, self.u)
        # print("V: ", v)

    def calculate_matrix(self):
        temp = np.identity(4, dtype=np.float64)

        temp[0][3] = self.local[0]
        temp[1][3] = self.local[1]
        temp[2][3] = self.local[2]
        self.model_matrix = temp
        # print("model_matrix:\n", model_matrix)

        # finishing calculating model matrix test

        temp = np.identity(4, dtype=np.float64)  # calculate T matrix, save as temp
        for i in range(0, 3):
            temp[i][3] = -self.camera[i]
        T = temp
        # print("T_matrix: \n", T)

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
        # print("R_matrix: \n", R)
        self.view_matrix = R @ T
        # print("view_matrix: \n", view_matrix)

        # finishing calculating view matrix

        temp = np.zeros((4, 4), dtype=np.float64)
        temp[0][0] = self.near / self.width
        temp[1][1] = self.near / self.width
        temp[2][2] = self.far / (self.far - self.near)
        temp[2][3] = - (self.far * self.near / (self.far - self.near))
        temp[3][2] = 1

        self.pers_matrix = temp
        # print("pers_matrix: \n", pers_matrix)

        # finishing calculating perspective matrix
        self.final_matrix = self.pers_matrix @ self.view_matrix
        # print("Final_matrix: \n", final_matrix)


def calculate_vertex(model, observer):
    '''
    calculate final vertex of a model under a certain observe parameter
    :param model:
    :param observer:
    :return:
    '''
    for i, v in enumerate(model.raw_vertex):
        v = observer.pers_matrix @ observer.view_matrix @ v
        # print("i = ", i, " ", v)
        v[0] = v[0] / v[3]
        v[1] = v[1] / v[3]
        # print(v[0], v[1])
        model.final_vertex.append([v[0], v[1]])
    # print("Calculated_vertex: \n", final_vertex)


def backface_culling(model, observer):
    '''
    Applying back-face culling on certain model under a certain observe parameter
    :param model:
    :param observer:
    :return:
    '''
    # determine visible polygons under certain observer parameter.
    model.view_vertex = []
    for i, v in enumerate(model.raw_vertex):
        v = observer.pers_matrix @ observer.view_matrix @ v  # vertex in view space
        model.view_vertex.append(v)
    # print("view vertex:\n", view_vertex)

    for p in model.raw_polygon:
        # print("P: \n", p)

        v1 = np.subtract(model.view_vertex[p[2] - 1], model.view_vertex[p[1] - 1])
        v2 = np.subtract(model.view_vertex[p[3] - 1], model.view_vertex[p[2] - 1])

        # print("V1 = ", v1, " v2 = ", v2)

        # print(type(v1[:-1]))
        v1 = v1[:-1]
        v2 = v2[:-1]
        Pn = np.cross(v1, v2)
        # print("Pn = ", Pn)

        if Pn[2] > 0:
            model.final_polygon.append(p)

    # print("final_polygon: \n", final_polygon)




if __name__ == "__main__":

    m1 = Model()
    m1.load_model('./queen.d.txt')
    # print("initial vertex:", m1.raw_vertex)
    # print("initial polygon:", m1.raw_polygon)
    # load_model()  # initiated model

    o1 = Observer()
    o1.set_modeling_matrix([0, 0, 0])  # input local-to-world parameter
    o1.set_viewing_matrix([20, 0, -5], [-1, -1, 0]) # input camera position and up-vector parameter
    o1.set_perspective_matrix(10, 80, 10)  # input Near & far volume and width
    o1.set_project_ref([0, 0, 0])  # input project reference

    o1.calculate_uvn()
    o1.calculate_matrix()

    calculate_vertex(m1, o1)

    backface_culling(m1, o1)

    m1.zoom_model(1000, 450)

    print(m1.final_polygon)

    window = pyglet.window.Window(1920, 1080, resizable=True)
    '''
    label = pyglet.text.Label("Hello World",
                              font_name="Times New Roman",
                              font_size=36,
                              x=window.width // 2,
                              y=window.height // 2,
                              anchor_x="center",
                              anchor_y="center")
    '''

    @window.event
    def on_draw():
        '''
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glBegin(GL_LINES)
        glVertex2f(202, 25)
        glVertex2f(49, 8)
        glEnd()
        '''
        window.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        for p in m1.final_polygon:
            """
            using final_popygon to enable backface culling
            using raw_popygon to disable backface culling
            """
            num = p[0]
            # print(num)
            p = p[1:]  # delete num
            # print(p)
            for i in range(num):
                if i == num - 1:
                    '''
                    Warning: 
                    to Visit proper vertex, you need to 
                    add -1 on index since the vertex are labeled start by 1, not 0.
                    '''
                    x1 = m1.final_vertex[p[i] - 1][0]
                    y1 = m1.final_vertex[p[i] - 1][1]
                    x2 = m1.final_vertex[p[0] - 1][0]
                    y2 = m1.final_vertex[p[0] - 1][1]
                else:
                    x1 = m1.final_vertex[p[i] - 1][0]
                    y1 = m1.final_vertex[p[i] - 1][1]
                    x2 = m1.final_vertex[p[i + 1] - 1][0]
                    y2 = m1.final_vertex[p[i + 1] - 1][1]
                glBegin(GL_LINE_LOOP)
                glVertex2f(x1, y1)
                glVertex2f(x2, y2)
                # print("x1 = ", x1, "y1 = ", y1, "\n")
                # print("x2 = ", x2, "y2 = ", y2, "\n")
                glEnd()

    pyglet.app.run()
