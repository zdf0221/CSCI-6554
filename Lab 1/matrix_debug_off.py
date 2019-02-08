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

# initializing matrices
model_matrix = np.identity(4, dtype=np.float64)
view_matrix = np.zeros(4, dtype=np.float64)
pers_matrix = np.zeros(4, dtype=np.float64)
final_matrix = np.zeros(4, dtype=np.float64)


def load_model():
    global raw_vertex, raw_polygon

    with open("./queen.d.txt") as f:
        read_data = f.read()
    # tying to read data and doing data cleaning
    data = read_data.replace("\t", " ").replace("data", "").split("\n")
    try:
        data.remove("")
    except IOError:
        print("Failed to open data file!")
    temp = data[0].split(" ")
    temp = [x for x in temp if x]  # filter the duplicated empty element.
    point_number = temp[0]
    polygon_number = temp[1]
    data = data[1:]  # trim the first 'data'

    for i, val in enumerate(data):
        if i < int(point_number):  # save vertex
            raw_vertex.append(val.split(" "))
        else:  # save polygon
            raw_polygon.append(val.split(" "))

    for i, v in enumerate(raw_vertex):
        temp = [float(x) for x in v if x]  # filter the duplicated empty element.
        temp.append(1)  # add 1 dimensions for easy matrix calculating
        raw_vertex[i] = temp

    for i, p in enumerate(raw_polygon):
        temp = [int(x) for x in p if x]  # filter the duplicated empty element.
        raw_polygon[i] = temp


# set parameters


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


# calculating


def calculate_uvn():
    global up_vector, u, v, n
    n = np.zeros(3, dtype=np.float64)
    n = np.subtract(n, camera)  # Warning! this is n - camera(Pref - c), not the camera - n!
    n /= np.linalg.norm(n)  # divided by the magnitude of vector N

    u = np.zeros(3, dtype=np.float64)
    temp = np.cross(n, up_vector)  # calculate the N x V'
    temp /= np.linalg.norm(temp)  # divided by |N x V'|
    u = temp

    v = np.cross(n, u)  # V = N x U


def calculate_matrix():
    global model_matrix, view_matrix, pers_matrix, final_matrix, camera, u, v, n, local, near, far, width
    temp = np.identity(4, dtype=np.float64)

    temp[0][3] = local[0]
    temp[1][3] = local[1]
    temp[2][3] = local[2]
    model_matrix = temp

    # finishing calculating model matrix

    temp = np.identity(4, dtype=np.float64)  # calculate T matrix, save as temp
    for i in range(0, 3):
        temp[i][3] = -camera[i]
    T = temp

    temp = np.identity(4, dtype=np.float64)  # calculate R matrix, save as temp
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

    view_matrix = R @ T  # M_view = R @ T(matrix multiplication)

    # finishing calculating view matrix

    temp = np.zeros((4, 4), dtype=np.float64)
    temp[0][0] = near / width
    temp[1][1] = near / width
    temp[2][2] = far / (far - near)
    temp[2][3] = - (far * near / (far - near))
    temp[3][2] = 1

    pers_matrix = temp

    # finishing calculating perspective matrix

    final_matrix = pers_matrix @ view_matrix


def calculate_vertex():
    global raw_vertex, raw_polygon, final_vertex, final_matrix

    for i, v in enumerate(raw_vertex):
        v = pers_matrix @ view_matrix @ v  # applied matrix on raw vertex data
        v[0] = v[0] / v[3]
        v[1] = v[1] / v[3]
        final_vertex.append([v[0], v[1]])  # vertices on screen space


def backface_culling():
    global raw_vertex, raw_polygon, final_polygon
    view_vertex = []
    for i, v in enumerate(raw_vertex):
        v = pers_matrix @ view_matrix @ v  # vertex in view space
        view_vertex.append(v)

    for p in raw_polygon:
        v1 = np.subtract(view_vertex[p[2] - 1], view_vertex[p[1] - 1])  # calculating 2 vector on polygon
        v2 = np.subtract(view_vertex[p[3] - 1], view_vertex[p[2] - 1])
        v1 = v1[:-1]  # discard the 4th dimension
        v2 = v2[:-1]  # discard the 4th dimension
        Pn = np.cross(v1, v2)  # making cross multiplication to generate normal vector

        if Pn[2] > 0:  # if normal vector's Z > 0
            final_polygon.append(p)  # polygon is visible


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

    @window.event
    def on_draw():
        window.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        for p in final_polygon:
            """
            using final_popygon to enable backface culling
            using raw_popygon to disable backface culling
            """
            num = p[0]
            p = p[1:]  # delete num
            amp = 1000  # amplifier parameter, making graph bigger
            shift = 350  # shift into screen center
            for i in range(num):
                if i == num - 1:
                    '''
                    Warning! 
                    To Visit correct vertex, you need to 
                    add -1 on index since the vertex are 
                    labeled start by 1, not 0.
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
                glBegin(GL_LINES)
                glVertex2f(x1, y1)
                glVertex2f(x2, y2)
                glEnd()

    pyglet.app.run()
