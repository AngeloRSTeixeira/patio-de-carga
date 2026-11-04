from OpenGL.GL import *


class OpenGLUtils(object):
    """Métodos estáticos para compilar shaders e ligar programas (seção 2.2)."""

    @staticmethod
    def initializeShader(shaderCode, shaderType):

        # versão exigida do OpenGL/GLSL
        shaderCode = "#version 330\n" + shaderCode

        # cria um shader vazio e retorna a referência
        shaderRef = glCreateShader(shaderType)
        # guarda o código-fonte no shader
        glShaderSource(shaderRef, shaderCode)
        # compila o código-fonte
        glCompileShader(shaderRef)

        # a compilação deu certo?
        compileSuccess = glGetShaderiv(shaderRef, GL_COMPILE_STATUS)
        if not compileSuccess:
            # recupera a mensagem de erro
            errorMessage = glGetShaderInfoLog(shaderRef)
            # libera a memória usada pelo shader
            glDeleteShader(shaderRef)
            # converte bytes em texto
            errorMessage = "\n" + errorMessage.decode("utf-8")
            # interrompe o programa e mostra o erro
            raise Exception(errorMessage)

        # compilação bem-sucedida
        return shaderRef

    @staticmethod
    def initializeProgram(vertexShaderCode, fragmentShaderCode):

        # compila os dois shaders
        vertexShaderRef = OpenGLUtils.initializeShader(
            vertexShaderCode, GL_VERTEX_SHADER)
        fragmentShaderRef = OpenGLUtils.initializeShader(
            fragmentShaderCode, GL_FRAGMENT_SHADER)

        # cria um programa vazio
        programRef = glCreateProgram()

        # anexa os shaders compilados
        glAttachShader(programRef, vertexShaderRef)
        glAttachShader(programRef, fragmentShaderRef)

        # liga o vertex shader ao fragment shader
        glLinkProgram(programRef)

        # a ligação deu certo?
        linkSuccess = glGetProgramiv(programRef, GL_LINK_STATUS)
        if not linkSuccess:
            errorMessage = glGetProgramInfoLog(programRef)
            glDeleteProgram(programRef)
            errorMessage = "\n" + errorMessage.decode("utf-8")
            raise Exception(errorMessage)

        # ligação bem-sucedida
        return programRef

    # mostra informações do sistema (útil para depuração)
    @staticmethod
    def printSystemInfo():
        print("  Vendor: " + glGetString(GL_VENDOR).decode("utf-8"))
        print("Renderer: " + glGetString(GL_RENDERER).decode("utf-8"))
        print("OpenGL version supported: " +
              glGetString(GL_VERSION).decode("utf-8"))
        print("  GLSL version supported: " +
              glGetString(GL_SHADING_LANGUAGE_VERSION).decode("utf-8"))
