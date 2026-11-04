import pygame
from OpenGL.GL import *


class Texture(object):
    """Imagem carregada numa textura da GPU (seção 5.1)."""

    def __init__(self, fileName=None, properties={}):

        # objeto do pygame que guarda os pixels
        self.surface = None

        # referência de uma textura disponível na GPU
        self.textureRef = glGenTextures(1)

        # valores padrão das propriedades
        self.properties = {
            "magFilter": GL_LINEAR,
            "minFilter": GL_LINEAR_MIPMAP_LINEAR,
            "wrap": GL_REPEAT,
        }

        # sobrescreve os valores padrão
        self.setProperties(properties)

        if fileName is not None:
            self.loadImage(fileName)
            self.uploadData()

    # carrega a imagem de um arquivo
    def loadImage(self, fileName):
        self.surface = pygame.image.load(fileName)

    def setProperties(self, props):
        for name, data in props.items():
            if name in self.properties.keys():
                self.properties[name] = data
            else:
                raise Exception("Texture has no property with name: " + name)

    # envia os pixels para a GPU
    def uploadData(self):

        width = self.surface.get_width()
        height = self.surface.get_height()

        # converte a imagem num buffer de bytes (invertida em y)
        pixelData = pygame.image.tostring(self.surface, "RGBA", 1)

        # seleciona a textura usada pelas funções seguintes
        glBindTexture(GL_TEXTURE_2D, self.textureRef)

        # envia os pixels
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, pixelData)

        # gera as versões reduzidas (mipmaps)
        glGenerateMipmap(GL_TEXTURE_2D)

        # filtros de ampliação e redução
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                        self.properties["magFilter"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                        self.properties["minFilter"])

        # o que acontece com coordenadas fora de [0, 1]
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,
                        self.properties["wrap"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,
                        self.properties["wrap"])

        # cor de borda branca; importante para as sombras
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1, 1, 1, 1])
