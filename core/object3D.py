import numpy

from core.matrix import Matrix


class Object3D(object):
    """Nó do grafo de cena: matriz de transformação, pai e filhos
    (seções 4.2, 5.6 e 6.2)."""

    def __init__(self):
        self.transform = Matrix.makeIdentity()
        self.parent = None
        self.children = []

    def add(self, child):
        self.children.append(child)
        child.parent = self

    def remove(self, child):
        self.children.remove(child)
        child.parent = None

    # transformação deste objeto em relação à raiz do grafo de cena
    def getWorldMatrix(self):
        if self.parent is None:
            return self.transform
        else:
            return self.parent.getWorldMatrix() @ self.transform

    # lista única com todos os descendentes
    def getDescendantList(self):
        descendants = []
        nodesToProcess = [self]
        while len(nodesToProcess) > 0:
            node = nodesToProcess.pop(0)
            descendants.append(node)
            nodesToProcess = node.children + nodesToProcess
        return descendants

    # aplica transformações geométricas
    #   localCoord=True: em relação aos eixos do próprio objeto
    #   localCoord=False: em relação aos eixos do pai
    def applyMatrix(self, matrix, localCoord=True):
        if localCoord:
            self.transform = self.transform @ matrix
        else:
            self.transform = matrix @ self.transform

    def translate(self, x, y, z, localCoord=True):
        m = Matrix.makeTranslation(x, y, z)
        self.applyMatrix(m, localCoord)

    def rotateX(self, angle, localCoord=True):
        m = Matrix.makeRotationX(angle)
        self.applyMatrix(m, localCoord)

    def rotateY(self, angle, localCoord=True):
        m = Matrix.makeRotationY(angle)
        self.applyMatrix(m, localCoord)

    def rotateZ(self, angle, localCoord=True):
        m = Matrix.makeRotationZ(angle)
        self.applyMatrix(m, localCoord)

    def scale(self, s, localCoord=True):
        m = Matrix.makeScale(s)
        self.applyMatrix(m, localCoord)

    # posição = última coluna da matriz de transformação
    def getPosition(self):
        return [self.transform[0, 3],
                self.transform[1, 3],
                self.transform[2, 3]]

    def getWorldPosition(self):
        worldTransform = self.getWorldMatrix()
        return [worldTransform[0, 3],
                worldTransform[1, 3],
                worldTransform[2, 3]]

    def setPosition(self, position):
        # ajuste: o livro usa itemset(), removido no numpy 2.0
        self.transform[0, 3] = position[0]
        self.transform[1, 3] = position[1]
        self.transform[2, 3] = position[2]

    # mantém a posição e faz o objeto "olhar" para o alvo
    def lookAt(self, targetPosition):
        self.transform = Matrix.makeLookAt(self.getWorldPosition(),
                                           targetPosition)

    # submatriz 3x3 com a rotação
    def getRotationMatrix(self):
        return numpy.array([self.transform[0][0:3],
                            self.transform[1][0:3],
                            self.transform[2][0:3]])

    # direção para onde o objeto aponta (eixo -z local)
    def getDirection(self):
        forward = numpy.array([0, 0, -1])
        return list(self.getRotationMatrix() @ forward)

    def setDirection(self, direction):
        position = self.getPosition()
        targetPosition = [position[0] + direction[0],
                          position[1] + direction[1],
                          position[2] + direction[2]]
        self.lookAt(targetPosition)
