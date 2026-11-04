import pygame
from OpenGL.GL import *

from core.texture import Texture


class RenderTarget(object):
    """Framebuffer que renderiza para uma textura (seção 5.9)."""

    def __init__(self, resolution=[512, 512], texture=None, properties={}):

        # devem ser iguais às dimensões da textura
        self.width, self.height = resolution

        if texture is not None:
            self.texture = texture
        else:
            self.texture = Texture(None, {
                "magFilter": GL_LINEAR,
                "minFilter": GL_LINEAR,
                "wrap": GL_CLAMP_TO_EDGE,
            })
            self.texture.setProperties(properties)
            self.texture.surface = pygame.Surface(resolution)
            self.texture.uploadData()

        # cria o framebuffer
        self.framebufferRef = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebufferRef)

        # o buffer de cor usa esta textura
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                             self.texture.textureRef, 0)

        # buffer para guardar a profundidade
        depthBufferRef = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, depthBufferRef)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT,
                              self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                                  GL_RENDERBUFFER, depthBufferRef)

        # confere o framebuffer
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Framebuffer status error")

        # volta a renderizar na janela
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
