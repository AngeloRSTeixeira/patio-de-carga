from OpenGL.GL import *
import numpy


class Attribute(object):
    """Dados de vértice guardados num buffer da GPU (seção 2.3)."""

    def __init__(self, dataType, data):

        # tipo dos elementos: int | float | vec2 | vec3 | vec4
        self.dataType = dataType

        # lista de dados a ser guardada no buffer
        self.data = data

        # referência de um buffer disponível na GPU
        self.bufferRef = glGenBuffers(1)

        # envia os dados imediatamente
        self.uploadData()

    # envia os dados para um buffer da GPU
    def uploadData(self):

        # converte para array numpy de floats de 32 bits
        data = numpy.array(self.data).astype(numpy.float32)

        # seleciona o buffer usado pelas funções seguintes
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferRef)

        # guarda os dados no buffer selecionado
        glBufferData(GL_ARRAY_BUFFER, data.ravel(), GL_STATIC_DRAW)

    # associa uma variável do programa (shader) a este buffer
    def associateVariable(self, programRef, variableName):

        # referência da variável com esse nome no programa
        variableRef = glGetAttribLocation(programRef, variableName)

        # se o programa não usa a variável, sai
        if variableRef == -1:
            return

        # seleciona o buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferRef)

        # indica como os dados serão lidos do buffer para a variável
        if self.dataType == "int":
            glVertexAttribPointer(variableRef, 1, GL_INT, False, 0, None)
        elif self.dataType == "float":
            glVertexAttribPointer(variableRef, 1, GL_FLOAT, False, 0, None)
        elif self.dataType == "vec2":
            glVertexAttribPointer(variableRef, 2, GL_FLOAT, False, 0, None)
        elif self.dataType == "vec3":
            glVertexAttribPointer(variableRef, 3, GL_FLOAT, False, 0, None)
        elif self.dataType == "vec4":
            glVertexAttribPointer(variableRef, 4, GL_FLOAT, False, 0, None)
        else:
            raise Exception("Attribute " + variableName +
                            " has unknown type " + self.dataType)

        # os dados do buffer passam a alimentar a variável
        glEnableVertexAttribArray(variableRef)
