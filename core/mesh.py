from OpenGL.GL import *

from core.object3D import Object3D


class Mesh(Object3D):
    """Objeto visível: geometria + material + VAO (seção 4.2.3)."""

    def __init__(self, geometry, material):
        super().__init__()

        self.geometry = geometry
        self.material = material

        # este objeto deve ser renderizado?
        self.visible = True

        # associa os atributos da geometria às variáveis
        # do programa de shader guardado no material
        self.vaoRef = glGenVertexArrays(1)
        glBindVertexArray(self.vaoRef)
        for variableName, attributeObject in geometry.attributes.items():
            attributeObject.associateVariable(material.programRef,
                                              variableName)
        # desfaz a seleção do VAO
        glBindVertexArray(0)
