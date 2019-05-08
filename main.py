from common import shader
from common import GLInit
from OpenGL.GL import *
from glfw.GLFW import *
import numpy as np
import cv2 as cv
from Render.BGRender import BGRender
from Render.MeshRender import MeshRender


if __name__ == '__main__':
    window = GLInit.myGLInit(320, 320)
    backGround = BGRender(320, 320)
    mesh = MeshRender(center_proj=False)
    mesh2 = MeshRender(center_proj=True)

    while (glfwGetKey(window, GLFW_KEY_ESCAPE) != GLFW_PRESS and glfwWindowShouldClose(window) == 0):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearBufferfv(GL_COLOR, 0, (0.0, 0.0, 0.0, 1.0))

        backGround.load_img(cv.imread('0.png', cv.IMREAD_COLOR))
        backGround.draw()

        vertexList = []
        faceList = []
        with open('0.obj', 'r') as file:
            lines = file.readlines()
            for line in lines:
                data = line.split(' ')
                if data[0] == 'v':
                    vertexList.append([float(data[1]), float(data[2]), float(data[3])])
                if data[0] == 'f':
                    faceList.append([int(data[1]) - 1, int(data[2]) - 1, int(data[3]) - 1])
        vertex = np.zeros((len(vertexList), 3), dtype='float32')
        for i in range(len(vertexList)):
            vertex[i, 0] = vertexList[i][0] * 1000
            vertex[i, 1] = vertexList[i][1] * 1000
            vertex[i, 2] = vertexList[i][2] * 1000 + 100
        face = np.zeros((len(faceList), 3), dtype='int')
        for i in range(len(faceList)):
            face[i, 0] = faceList[i][0]
            face[i, 1] = faceList[i][1]
            face[i, 2] = faceList[i][2]

        mesh.load_data(vertex=vertex, face=face, uv=None, TextureImg=None)
        mesh.set_camera_orth(scale=1, u=0, v=0, height=320, width=320)
        mesh.draw()

        # cameraIn = np.identity(3, dtype='float32')
        # cameraIn[0, 2] = 160
        # cameraIn[1, 2] = 160
        # cameraIn[0, 0] = 100
        # cameraIn[1, 1] = 100
        # cameraEx = np.identity(4, dtype='float32')
        # mesh2.load_data(vertex=vertex, face=face, uv=None, TextureImg=None)
        # mesh2.set_camera_center(cameraIn=cameraIn, cameraEx=cameraEx, height=320, width=320)
        # mesh2.draw()

        glfwSwapBuffers(window)
        glfwPollEvents()

    glfwTerminate()
