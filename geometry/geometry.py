import numpy

from core.attribute import Attribute


class Geometry(object):
    """Conjunto de atributos de vértice (seções 4.3 e 6.3)."""

    def __init__(self):

        # objetos Attribute, indexados pelo nome da variável no shader
        self.attributes = {}

        # número de vértices
        self.vertexCount = None

    def addAttribute(self, dataType, variableName, data):
        self.attributes[variableName] = Attribute(dataType, data)

    def countVertices(self):
        # qualquer atributo tem um dado por vértice
        attrib = list(self.attributes.values())[0]
        self.vertexCount = len(attrib.data)

    # transforma os dados de posição (e as normais) com uma matriz
    def applyMatrix(self, matrix, variableName="vertexPosition"):

        oldPositionData = self.attributes[variableName].data
        newPositionData = []
        for oldPos in oldPositionData:
            # evita alterar as listas originais
            newPos = list(oldPos).copy()
            # coordenada homogênea
            newPos.append(1)
            newPos = matrix @ newPos
            newPos = list(newPos[0:3])
            newPositionData.append(newPos)
        self.attributes[variableName].data = newPositionData

        # as normais giram apenas com a parte de rotação da matriz
        rotationMatrix = numpy.array([matrix[0][0:3],
                                      matrix[1][0:3],
                                      matrix[2][0:3]])
        for normalName in ["vertexNormal", "faceNormal"]:
            if normalName in self.attributes:
                oldNormalData = self.attributes[normalName].data
                newNormalData = []
                for oldNormal in oldNormalData:
                    newNormal = rotationMatrix @ numpy.array(oldNormal)
                    newNormalData.append(list(newNormal))
                self.attributes[normalName].data = newNormalData
                self.attributes[normalName].uploadData()

        # os novos dados precisam ser enviados
        self.attributes[variableName].uploadData()

    # junta os atributos de outra geometria a esta
    #   (as duas precisam ter atributos com os mesmos nomes)
    def merge(self, otherGeometry):
        for variableName, attributeObject in self.attributes.items():
            attributeObject.data += otherGeometry.attributes[variableName].data
            attributeObject.uploadData()
        self.countVertices()
