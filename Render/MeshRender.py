from OpenGL.GL import *
from glfw.GLFW import *
from pyRender.common import shader
import numpy as np
import cv2 as cv
import os


class MeshRender:
    def __init__(self, center_proj=True):
        self.center_proj = center_proj
        if center_proj:
            self.programID = shader.loadShaders(os.path.dirname(__file__) + '/shader/mesh_center_proj.vertexshader', os.path.dirname(__file__) + '/shader/mesh_center_proj.fragmentshader')
        else:
            self.programID = shader.loadShaders(os.path.dirname(__file__) + '/shader/mesh_orth_proj.vertexshader', os.path.dirname(__file__) + '/shader/mesh_orth_proj.fragmentshader')

        self.VertexArrayID = glGenVertexArrays(1)

        self.VertexBuffer = glGenBuffers(1)
        self.UvBuffer = glGenBuffers(1)
        self.NormalBuffer = glGenBuffers(1)
        self.TextureBuffer = glGenTextures(1)
        self.TextureImg = np.ones((8, 8, 3), dtype='uint8')
        self.height = 8
        self.width = 8

    def load_data(self, vertex, face, uv=None, faceUV=None, TextureImg=None):
        self.faceNum = np.size(face, 0)
        vertexNum = np.size(vertex, 0)
        vertex3 = np.zeros((3 * self.faceNum, 3), dtype='float32')
        normal = np.zeros((vertexNum, 3), dtype='float32')
        normal3 = np.zeros((3 * self.faceNum, 3), dtype='float32')
        for idx in range(self.faceNum):
            vertex3[3 * idx + 0, :] = vertex[face[idx, 0], :]
            vertex3[3 * idx + 1, :] = vertex[face[idx, 1], :]
            vertex3[3 * idx + 2, :] = vertex[face[idx, 2], :]
            v1 = vertex[face[idx, 1], :] - vertex[face[idx, 0], :]
            v2 = vertex[face[idx, 2], :] - vertex[face[idx, 1], :]
            n = np.array([v1[1] * v2[2] - v1[2] * v2[1],
                          v1[2] * v2[0] - v1[0] * v2[2],
                          v1[0] * v2[1] - v1[1] * v2[0]],
                         dtype='float32')
            normal[face[idx, 0], :] += n
            normal[face[idx, 1], :] += n
            normal[face[idx, 2], :] += n
        for i in range(vertexNum):
            normal[i, :] /= np.linalg.norm(normal[i, :])
        for idx in range(self.faceNum):
            normal3[3 * idx + 0, :] = normal[face[idx, 0], :]
            normal3[3 * idx + 1, :] = normal[face[idx, 1], :]
            normal3[3 * idx + 2, :] = normal[face[idx, 2], :]
        if uv is None or TextureImg is None or faceUV is None:
            self.TextureImg = np.ones((8, 8, 3), dtype='uint8') * 128
            self.height = 8
            self.width = 8
            uv = np.zeros((np.size(vertex, 0), 2), dtype='float32')
            faceUV = face
        else:
            self.TextureImg = cv.flip(TextureImg, 0)
            self.height = np.size(TextureImg, 0)
            self.width = np.size(TextureImg, 1)
        uv3 = np.zeros((3 * self.faceNum, 2), dtype='float32')
        for idx in range(self.faceNum):
            uv3[3 * idx + 0, :] = uv[faceUV[idx, 0], :]
            uv3[3 * idx + 1, :] = uv[faceUV[idx, 1], :]
            uv3[3 * idx + 2, :] = uv[faceUV[idx, 2], :]

        # print(vertex3)
        # print(uv3)
        # print(normal3)
        glBindVertexArray(self.VertexArrayID)
        glBindBuffer(GL_ARRAY_BUFFER, self.VertexBuffer)
        glBufferData(GL_ARRAY_BUFFER, vertex3.nbytes, vertex3, GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.UvBuffer)
        glBufferData(GL_ARRAY_BUFFER, uv3.nbytes, uv3, GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.NormalBuffer)
        glBufferData(GL_ARRAY_BUFFER, normal3.nbytes, normal3, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.VertexBuffer)
        glVertexAttribPointer(
            0,  # attribute
            3,  # size
            GL_FLOAT,  # type
            GL_FALSE,  # normalized?
            0,  # stride
            None  # array buffer offset
        )
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.UvBuffer)
        glVertexAttribPointer(
            1,  # attribute
            2,  # size
            GL_FLOAT,  # type
            GL_FALSE,  # normalized?
            0,  # stride
            None  # array buffer offset
        )
        glEnableVertexAttribArray(2)
        glBindBuffer(GL_ARRAY_BUFFER, self.NormalBuffer)
        glVertexAttribPointer(
            2,  # attribute
            3,  # size
            GL_FLOAT,  # type
            GL_FALSE,  # normalized?
            0,  # stride
            None  # array buffer offset
        )
        glBindVertexArray(0)

    def bind_texture(self):
        glBindVertexArray(self.VertexArrayID)
        glBindTexture(GL_TEXTURE_2D, self.TextureBuffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_BGR, GL_UNSIGNED_BYTE, self.TextureImg)
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

    def set_camera_center(self, cameraIn, cameraEx, height, width):
        if not self.center_proj:
            raise RuntimeError('This Render is orthogonal projection!')
        assert cameraIn.shape == (3, 3), 'shape of cameraIn should be (3, 3), get {}'.format(cameraIn.shape)
        assert cameraEx.shape == (4, 4), 'shape of cameraEx should be (4, 4), get {}'.format(cameraEx.shape)
        camera = np.zeros((4, 4), dtype='float32')
        camera[3, 3] = 1
        camera[2, 2] = 1
        camera[0, 0] = cameraIn[0, 0] * 2 / width
        camera[1, 1] = -cameraIn[1, 1] * 2 / height
        camera[0, 2] = cameraIn[0, 2] * 2 / width - 1.0
        camera[1, 2] = -cameraIn[1, 2] * 2 / height + 1.0
        camera = np.matmul(camera, cameraEx)
        # print(camera)

        # cameraR = cameraEx[0:3, 0:3]

        glUseProgram(self.programID)
        cameraInID = glGetUniformLocation(self.programID, "cameraIn")
        glUniformMatrix3fv(cameraInID, 1, GL_FALSE, cameraIn.transpose())
        rotationID = glGetUniformLocation(self.programID, "Rotation")
        glUniformMatrix3fv(rotationID, 1, GL_FALSE, cameraEx[0:3, 0:3].transpose())
        transID = glGetUniformLocation(self.programID, "Translation")
        glUniform3f(transID, cameraEx[0, 3], cameraEx[1, 3], cameraEx[2, 3])
        heightID = glGetUniformLocation(self.programID, "height")
        glUniform1f(heightID, height)
        widthID = glGetUniformLocation(self.programID, "width")
        glUniform1f(widthID, width)
        glUseProgram(0)
        # glUseProgram(self.programID)
        # MatrixID = glGetUniformLocation(self.programID, "MVP")
        # glUniformMatrix4fv(MatrixID, 1, GL_FALSE, camera)
        # MatrixID2 = glGetUniformLocation(self.programID, "Rotation")
        # glUniformMatrix3fv(MatrixID2, 1, GL_FALSE, cameraR)
        # MatrixID3 = glGetUniformLocation(self.programID, "Translation")
        # glUniform3f(MatrixID3, cameraEx[0, 3], cameraEx[1, 3], cameraEx[2, 3])
        # glUseProgram(0)
        return camera

    def set_camera_orth(self, scale, u, v, height, width):
        if self.center_proj:
            raise RuntimeError('This Render is center projection!')

        glUseProgram(self.programID)

        TempFloatID = glGetUniformLocation(self.programID, "Scale")
        glUniform1f(TempFloatID, scale)
        TempFloatID = glGetUniformLocation(self.programID, "U")
        glUniform1f(TempFloatID, u)
        TempFloatID = glGetUniformLocation(self.programID, "V")
        glUniform1f(TempFloatID, v)
        TempFloatID = glGetUniformLocation(self.programID, "Width")
        glUniform1f(TempFloatID, width)
        TempFloatID = glGetUniformLocation(self.programID, "Height")
        glUniform1f(TempFloatID, height)

        glUseProgram(0)

    def draw(self):
        self.bind_texture()
        glBindVertexArray(self.VertexArrayID)
        glUseProgram(self.programID)
        glDrawArrays(GL_TRIANGLES, 0, 3 * self.faceNum)
        glUseProgram(0)
        glBindVertexArray(0)
