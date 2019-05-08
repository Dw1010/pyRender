from OpenGL.GL import *


def compile_shader(shader_file_path, shader_type):
    ShaderId = glCreateShader(shader_type)
    shaderCode = ''
    with open(shader_file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            shaderCode = shaderCode + line
    # print(shaderCode)
    # print(type(shaderCode))
    # Compile Shader
    print('Compiling shader : {}'.format(shader_file_path))
    glShaderSource(ShaderId, shaderCode)
    glCompileShader(ShaderId)

    # Check Shader
    # Result = glGetShaderiv(ShaderId, GL_COMPILE_STATUS)
    InfoLogLength = glGetShaderiv(ShaderId, GL_INFO_LOG_LENGTH)
    if (InfoLogLength > 0):
        VertexShaderErrorMessage = glGetShaderInfoLog(ShaderId)
        print(VertexShaderErrorMessage)
        raise SyntaxError('error from shader: {}'.format(shader_file_path))
    return ShaderId


def loadShaders(vertex_file_path, fragment_file_path):
    VertexShaderID = compile_shader(vertex_file_path, GL_VERTEX_SHADER)
    FragmentShaderID = compile_shader(fragment_file_path, GL_FRAGMENT_SHADER)

    # Link the program
    print('Linking program')
    ProgramID = glCreateProgram()
    glAttachShader(ProgramID, VertexShaderID)
    glAttachShader(ProgramID, FragmentShaderID)
    glLinkProgram(ProgramID)

    # Check the program
    # Result = glGetProgramiv(ProgramID, GL_LINK_STATUS)
    InfoLogLength = glGetProgramiv(ProgramID, GL_INFO_LOG_LENGTH)
    if (InfoLogLength > 0):
        ProgramErrorMessage = glGetProgramInfoLog(ProgramID)
        print(ProgramErrorMessage)
        raise RuntimeError('program error')

    glDetachShader(ProgramID, VertexShaderID)
    glDetachShader(ProgramID, FragmentShaderID)

    glDeleteShader(VertexShaderID)
    glDeleteShader(FragmentShaderID)

    return ProgramID
