
import numpy as np
import cv2 as cv

import sys
sys.path.append('../')

from OpenGL.GL import *
from glfw.GLFW import *
from pyRender.common import myGLInit
from pyRender.Render import BGRender
from pyRender.Render import MeshRender


if __name__ == '__main__':
    img_size = 320

    window = myGLInit(img_size, img_size)
    backGround = BGRender(img_size, img_size)
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
        mesh.set_camera_orth(scale=1, u=0, v=0, height=img_size, width=img_size)
        mesh.draw()

        # cameraIn = np.identity(3, dtype='float32')
        # cameraIn[0, 2] = 160
        # cameraIn[1, 2] = 160
        # cameraIn[0, 0] = 100
        # cameraIn[1, 1] = 100
        # cameraEx = np.identity(4, dtype='float32')
        # mesh2.load_data(vertex=vertex, face=face, uv=None, TextureImg=None)
        # mesh2.set_camera_center(cameraIn=cameraIn, cameraEx=cameraEx, height=img_size, width=img_size)
        # mesh2.draw()

        data = glReadPixels(0, 0, img_size, img_size, GL_BGRA, GL_FLOAT, outputType=None)
        data = data.reshape(img_size, img_size, -1)
        data = np.flip(data, 0)
        img = (255 * data[..., :3]).astype(np.uint8)
        mask = (255 - 255 * data[..., 3:]).astype(np.uint8)

        data = glReadPixels(0, 0, img_size, img_size, GL_DEPTH_COMPONENT, GL_FLOAT, outputType=None)
        z = data.reshape(img_size, img_size)
        z = np.flip(z, 0)

        glfwSwapBuffers(window)
        glfwPollEvents()

    glfwTerminate()
