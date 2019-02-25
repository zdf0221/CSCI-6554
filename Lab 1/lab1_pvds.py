# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Matrix
   Description :
   Author :       zdf's desktop
   date：          2019/2/4
-------------------------------------------------
   Change Activity:
                   2019/2/4:15:22
-------------------------------------------------
"""

import numpy as np
from pyglet.gl import *
from OpenGL.GL import *


local = []
camera = []
up_vector = []
p_ref = []

raw_vertex = []
raw_polygon = []
final_vertex = []  # vertex in screen space
final_polygon = []  # viewing polygon after backface-culling

near = 0
far = 0
width = 0

u = v = n = []

model_matrix = np.identity(4, dtype=np.float64)
# print("model_matrix:", model_matrix)
view_matrix = np.zeros(4, dtype=np.float64)
# print("view_matrix:", view_matrix)
pers_matrix = np.zeros(4, dtype=np.float64)
# print("pers_matrix:", pers_matrix)
final_matrix = np.zeros(4, dtype=np.float64)
# print("final_matrix: \n", final_matrix)


def load_model():
    global raw_vertex, raw_polygon

    with open("./queen.d.txt") as f:
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

    print("Point Number:" + point_number)
    print("Polygon Number:" + polygon_number)

    data = data[1:]  # trim the first data

    for i, val in enumerate(data):
        if i < int(point_number):
            raw_vertex.append(val.split(" "))
        else:
            raw_polygon.append(val.split(" "))

    print("raw_vertex: ", raw_vertex)
    # print("raw_polygon: ", raw_polygon)

    for i, v in enumerate(raw_vertex):
        temp = [float(x) for x in v if x]
        temp.append(1)
        raw_vertex[i] = temp

    for i, p in enumerate(raw_polygon):
        temp = [int(x) for x in p if x]
        raw_polygon[i] = temp

    print("raw_vertex: ", raw_vertex)
    # print("raw_polygon: ", raw_polygon)


def set_modeling_matrix(l):
    global local
    local = l


def set_viewing_matrix(c, up):
    global camera, up_vector
    camera = c
    up_vector = up


def set_perspective_parameter(n, f, h):
    global near, far, width
    near = n
    far = f
    width = h


def set_project_ref(p):
    global p_ref
    p_ref = p


def calculate_uvn():
    global up_vector, u, v, n
    n = np.zeros(3, dtype=np.float64)
    n = np.subtract(n, camera) # Warning! this is n - camera(Pref - c), not the backwards!
    print("camera:", camera)
    print("magnitude:", np.linalg.norm(n))
    n /= np.linalg.norm(n)  # calculate the magnitude of vector N
    print("N: ", n)

    u = np.zeros(3, dtype=np.float64)
    print("up-vector:", up_vector)
    temp = np.cross(n, up_vector)  # calculate the N x V'
    # print(np.linalg.norm(temp))
    temp /= np.linalg.norm(temp)  # divided by |N x V'|
    u = temp
    print("U: ", u)

    v = np.cross(n, u)
    print("V: ", v)


def calculate_matrix():
    global model_matrix, view_matrix, pers_matrix, final_matrix, camera, u, v, n, local, near, far, width
    temp = np.identity(4, dtype=np.float64)

    temp[0][3] = local[0]
    temp[1][3] = local[1]
    temp[2][3] = local[2]
    model_matrix = temp
    print("model_matrix:\n", model_matrix)

    # finishing calculating model matrix test

    temp = np.identity(4, dtype=np.float64)  # calculate T matrix, save as temp
    for i in range(0, 3):
        temp[i][3] = -camera[i]
    T = temp
    print("T_matrix: \n", T)

    temp = np.identity(4, dtype=np.float64)  # calculate R matrix, save as temp
    # print(type(n))
    temp[0][0] = u[0]
    temp[0][1] = u[1]
    temp[0][2] = u[2]
    temp[1][0] = v[0]
    temp[1][1] = v[1]
    temp[1][2] = v[2]
    temp[2][0] = n[0]
    temp[2][1] = n[1]
    temp[2][2] = n[2]

    R = temp
    print("R_matrix: \n", R)
    view_matrix = R @ T
    print("view_matrix: \n", view_matrix)

    # finishing calculating view matrix

    temp = np.zeros((4, 4), dtype=np.float64)
    temp[0][0] = near / width
    temp[1][1] = near / width
    temp[2][2] = far / (far - near)
    temp[2][3] = - (far * near / (far - near))
    temp[3][2] = 1

    pers_matrix = temp
    print("pers_matrix: \n", pers_matrix)

    # finishing calculating perspective matrix
    final_matrix = pers_matrix @ view_matrix
    # print("Final_matrix: \n", final_matrix)

    # print([8.0, 16.0, 30.0, 1] @ final_matrix)


def calculate_vertex():
    global raw_vertex, raw_polygon, final_vertex, final_matrix

    for i, v in enumerate(raw_vertex):
        v = pers_matrix @ view_matrix @ v
        print("i = ", i, " ", v)
        v[0] = v[0] / v[3]
        v[1] = v[1] / v[3]
        # print(v[0], v[1])
        final_vertex.append([v[0], v[1]])
    print("Calculated_vertex: \n", final_vertex)


def backface_culling():
    global raw_vertex, raw_polygon, final_polygon
    view_vertex = []
    for i, v in enumerate(raw_vertex):
        v = pers_matrix @ view_matrix @ v  # vertex in view space
        view_vertex.append(v)
    print("view vertex:\n", view_vertex)

    for p in raw_polygon:
        print("P: \n", p)

        v1 = np.subtract(view_vertex[p[2] - 1], view_vertex[p[1] - 1])
        v2 = np.subtract(view_vertex[p[3] - 1], view_vertex[p[2] - 1])

        print("V1 = ", v1, " v2 = ", v2)

        #print(np.cross([8.0, -6.0, 0.0], [0.0, -10.0, 0.0]))
        # print(type(v1[:-1]))
        v1 = v1[:-1]
        v2 = v2[:-1]
        Pn = np.cross(v1, v2)
        print("Pn = ", Pn)

        if Pn[2] > 0:
            final_polygon.append(p)

    print("final_polygon: \n", final_polygon)


if __name__ == "__main__":

    load_model()  # initiated model

    set_modeling_matrix([0, 0, 0])  # input local-to-world parameter
    set_viewing_matrix([10, 0, -5], [-1, -1, 0])  # input camera position and up-vector parameter
    set_perspective_parameter(10, 80, 10)  # input Near & far volume and width
    set_project_ref([0, 0, 0])  # input project reference

    calculate_uvn()
    calculate_matrix()
    calculate_vertex()

    backface_culling()

    window = pyglet.window.Window(1280, 720, resizable=True)
    label = pyglet.text.Label("Hello World",
                              font_name="Times New Roman",
                              font_size=36,
                              x=window.width // 2,
                              y=window.height // 2,
                              anchor_x="center",
                              anchor_y="center")


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
        #'''
        window.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        for p in final_polygon:
            """
            using final_popygon to enable backface culling
            using raw_popygon to disable backface culling
            """
            num = p[0]
            # print(num)
            p = p[1:]  # delete num
            # print(p)
            amp = 1000  # amplifier
            shift = 350 # shift into center
            for i in range(num):
                if i == num - 1:
                    '''
                    Warning: 
                    to Visit proper vertex, you need to 
                    add -1 on index since the vertex are labeled start by 1, not 0.
                    '''
                    x1 = final_vertex[p[i] - 1][0] * amp + shift
                    y1 = final_vertex[p[i] - 1][1] * amp + shift
                    x2 = final_vertex[p[0] - 1][0] * amp + shift
                    y2 = final_vertex[p[0] - 1][1] * amp + shift
                else:
                    x1 = final_vertex[p[i] - 1][0] * amp + shift
                    y1 = final_vertex[p[i] - 1][1] * amp + shift
                    x2 = final_vertex[p[i + 1] - 1][0] * amp + shift
                    y2 = final_vertex[p[i + 1] - 1][1] * amp + shift
                glBegin(GL_LINE_LOOP)
                glVertex2f(x1, y1)
                glVertex2f(x2, y2)
                # print("x1 = ", x1, "y1 = ", y1, "\n")
                # print("x2 = ", x2, "y2 = ", y2, "\n")
                glEnd()
        #'''

    pyglet.app.run()
