from OpenGL.GL import *


class Uniform(object):
    """Valor enviado do Python para uma variável uniform do shader
    (seções 2.4, 3.4, 5.3, 6.4.1 e 6.9.2)."""

    def __init__(self, dataType, data):

        # tipo: int | bool | float | vec2 | vec3 | vec4 | mat4 |
        #       sampler2D | Light | Shadow
        self.dataType = dataType

        # dado a ser enviado
        self.data = data

        # referência da variável no programa
        self.variableRef = None

    # obtém e guarda a(s) referência(s) da variável com esse nome
    def locateVariable(self, programRef, variableName):

        if self.dataType == "Light":
            # struct: uma referência para cada campo
            self.variableRef = {}
            for field in ["lightType", "color", "direction",
                          "position", "attenuation"]:
                self.variableRef[field] = glGetUniformLocation(
                    programRef, variableName + "." + field)

        elif self.dataType == "Shadow":
            self.variableRef = {}
            for field in ["lightDirection", "projectionMatrix",
                          "viewMatrix", "depthTexture",
                          "strength", "bias"]:
                self.variableRef[field] = glGetUniformLocation(
                    programRef, variableName + "." + field)

        else:
            self.variableRef = glGetUniformLocation(programRef, variableName)

    # envia o dado para a variável localizada
    def uploadData(self):

        # se o programa não usa a variável, sai
        if self.variableRef == -1:
            return

        if self.dataType == "int":
            glUniform1i(self.variableRef, self.data)

        elif self.dataType == "bool":
            glUniform1i(self.variableRef, self.data)

        elif self.dataType == "float":
            glUniform1f(self.variableRef, self.data)

        elif self.dataType == "vec2":
            glUniform2f(self.variableRef, self.data[0], self.data[1])

        elif self.dataType == "vec3":
            glUniform3f(self.variableRef,
                        self.data[0], self.data[1], self.data[2])

        elif self.dataType == "vec4":
            glUniform4f(self.variableRef, self.data[0], self.data[1],
                        self.data[2], self.data[3])

        elif self.dataType == "mat4":
            # GL_TRUE: os dados estão em linhas (numpy), não em colunas
            glUniformMatrix4fv(self.variableRef, 1, GL_TRUE, self.data)

        elif self.dataType == "sampler2D":
            textureObjectRef, textureUnitRef = self.data
            # ativa a unidade de textura
            glActiveTexture(GL_TEXTURE0 + textureUnitRef)
            # associa a textura à unidade ativa
            glBindTexture(GL_TEXTURE_2D, textureObjectRef)
            # envia o número da unidade para o sampler do shader
            glUniform1i(self.variableRef, textureUnitRef)

        elif self.dataType == "Light":
            glUniform1i(self.variableRef["lightType"], self.data.lightType)
            glUniform3f(self.variableRef["color"], self.data.color[0],
                        self.data.color[1], self.data.color[2])
            direction = self.data.getDirection()
            glUniform3f(self.variableRef["direction"],
                        direction[0], direction[1], direction[2])
            position = self.data.getPosition()
            glUniform3f(self.variableRef["position"],
                        position[0], position[1], position[2])
            glUniform3f(self.variableRef["attenuation"],
                        self.data.attenuation[0],
                        self.data.attenuation[1],
                        self.data.attenuation[2])

        elif self.dataType == "Shadow":
            direction = self.data.lightSource.getDirection()
            glUniform3f(self.variableRef["lightDirection"],
                        direction[0], direction[1], direction[2])

            glUniformMatrix4fv(self.variableRef["projectionMatrix"], 1,
                               GL_TRUE, self.data.camera.projectionMatrix)
            glUniformMatrix4fv(self.variableRef["viewMatrix"], 1,
                               GL_TRUE, self.data.camera.viewMatrix)

            # textura de profundidade numa unidade pouco usada (15)
            textureObjectRef = self.data.renderTarget.texture.textureRef
            textureUnitRef = 15
            glActiveTexture(GL_TEXTURE0 + textureUnitRef)
            glBindTexture(GL_TEXTURE_2D, textureObjectRef)
            glUniform1i(self.variableRef["depthTexture"], textureUnitRef)

            glUniform1f(self.variableRef["strength"], self.data.strength)
            glUniform1f(self.variableRef["bias"], self.data.bias)
