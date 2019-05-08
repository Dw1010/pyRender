from OpenGL.GL import *
from glfw.GLFW import *
import numpy as np


def myGLInit(Height, Width):
    if not glfwInit():
        raise RuntimeError('Failed to initialize GLFW')

    glfwWindowHint(GLFW_SAMPLES, 4)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)

    # Open a window and create its OpenGL context
    window = glfwCreateWindow(Width, Height, "MyRender", None, None)
    if window is None:
        glfwTerminate()
        raise RuntimeError('window is None')
    glfwMakeContextCurrent(window)

    # Initialize GLEW
    # Needed for core profile
    # if glewInit() != GLEW_OK:
    #     glfwTerminate()
    #     raise('Failed to initialize GLEW')

    glClearColor(0.0, 0.0, 0.0, 0.0)

    # Ensure we can capture the escape key being pressed below
    glfwSetInputMode(window, GLFW_STICKY_KEYS, GL_TRUE)

    # Enable depth test
    glEnable(GL_DEPTH_TEST)
    # Accept fragment if it closer to the camera than the former one
    glDepthFunc(GL_LESS)

    # Cull triangles which normal is not towards the camera
    glEnable(GL_CULL_FACE)
    return window
