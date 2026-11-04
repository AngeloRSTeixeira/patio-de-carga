from OpenGL.GL import *

from core.openGLUtils import OpenGLUtils
from core.uniform import Uniform


class Material(object):
    """Programa de shader + uniforms + configurações de renderização
    (seção 4.4.1)."""

    def __init__(self, vertexShaderCode, fragmentShaderCode):

        self.programRef = OpenGLUtils.initializeProgram(vertexShaderCode,
                                                        fragmentShaderCode)

        # objetos Uniform, indexados pelo nome da variável no shader
        self.uniforms = {}

        # presentes em quase todo shader; preenchidos pelo Renderer
        # a partir do Mesh e da Camera
        self.uniforms["modelMatrix"] = Uniform("mat4", None)
        self.uniforms["viewMatrix"] = Uniform("mat4", None)
        self.uniforms["projectionMatrix"] = Uniform("mat4", None)

        # configurações do OpenGL, indexadas pelo nome
        self.settings = {}
        self.settings["drawStyle"] = GL_TRIANGLES

    def addUniform(self, dataType, variableName, data):
        self.uniforms[variableName] = Uniform(dataType, data)

    # localiza todas as variáveis uniform no programa
    def locateUniforms(self):
        for variableName, uniformObject in self.uniforms.items():
            uniformObject.locateVariable(self.programRef, variableName)

    # configura o OpenGL; implementado pelas subclasses
    def updateRenderSettings(self):
        pass

    # define várias "propriedades" (uniforms e configurações)
    # de uma vez a partir de um dicionário
    def setProperties(self, properties):
        for name, data in properties.items():
            if name in self.uniforms.keys():
                self.uniforms[name].data = data
            elif name in self.settings.keys():
                self.settings[name] = data
            else:
                raise Exception("Material has no property named: " + name)
