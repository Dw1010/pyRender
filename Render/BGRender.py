from OpenGL.GL import *
from glfw.GLFW import *
import numpy as np
import cv2 as cv
import os

import sys
sys.path.append('../../')
from ..common.shader import loadShaders


class BGRender:
    def __init__(self, height, width):
        self.height = height
        self.width = width

        self.programID = loadShaders(os.path.dirname(__file__) + '/shader/background.vertexshader', os.path.dirname(__file__) + '/shader/background.fragmentshader')
        self.VertexArrayID = glGenVertexArrays(1)
        self.VertexBuffer = glGenBuffers(1)
        self.UvBuffer = glGenBuffers(1)
        self.TextureBuffer = glGenTextures(1)
        self.BGimg = np.ones((height, width, 3), dtype='uint8') * 255

        vertexs = np.array([[-1.0, -1.0, 0.999],
                            [+1.0, -1.0, 0.999],
                            [-1.0, +1.0, 0.999],
                            [+1.0, -1.0, 0.999],
                            [+1.0, +1.0, 0.999],
                            [-1.0, +1.0, 0.999]],
                           dtype='float32')
        uv = np.array([[0.0, 0.0],
                       [1.0, 0.0],
                       [0.0, 1.0],
                       [1.0, 0.0],
                       [1.0, 1.0],
                       [0.0, 1.0]],
                      dtype='float32')

        glBindVertexArray(self.VertexArrayID)

        glBindBuffer(GL_ARRAY_BUFFER, self.VertexBuffer)
        glBufferData(GL_ARRAY_BUFFER, vertexs.nbytes, vertexs, GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.UvBuffer)
        glBufferData(GL_ARRAY_BUFFER, uv.nbytes, uv, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.VertexBuffer)
        glVertexAttribPointer(
            0,  # attribute
            3,  # size
            GL_FLOAT,  # type
            GL_FALSE,  # normalized?
            0,  # stride
            None            # array buffer offset
        )

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.UvBuffer)
        glVertexAttribPointer(
            1,  # attribute
            2,  # size
            GL_FLOAT,  # type
            GL_FALSE,  # normalized?
            0,  # stride
            None                          # array buffer offset
        )
        glBindVertexArray(0)

    def load_img(self, img):
        self.BGimg = cv.resize(img, (self.width, self.height))
        self.BGimg = cv.flip(self.BGimg, 0)

    def bind_texture(self):
        glBindVertexArray(self.VertexArrayID)
        glBindTexture(GL_TEXTURE_2D, self.TextureBuffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_BGR, GL_UNSIGNED_BYTE, self.BGimg)
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        glUseProgram(self.programID)
        self.TextureID = glGetUniformLocation(self.programID, "myTextureSampler")
        # Bind our texture in Texture Unit 0
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.TextureBuffer)
        # Set our "myTextureSampler" sampler to use Texture Unit 0
        glUniform1i(self.TextureID, 1)
        glUseProgram(0)
        glBindVertexArray(0)

    def draw(self):
        self.bind_texture()
        glBindVertexArray(self.VertexArrayID)
        glUseProgram(self.programID)
        glDrawArrays(GL_TRIANGLES, 0, 3 * 2)
        glUseProgram(0)
        glBindVertexArray(0)
