import pygame
from OpenGL.GL import *

from core.mesh import Mesh
from light.light import Light
from light.shadow import Shadow


class Renderer(object):
    """Desenha a cena: passe de sombra + passe principal
    (seções 4.5, 5.9, 6.4 e 6.9.2)."""

    def __init__(self, clearColor=[0, 0, 0]):

        glEnable(GL_DEPTH_TEST)
        # necessário para o antialiasing
        glEnable(GL_MULTISAMPLE)
        # ajuste: guarda a cor de fundo, porque o passe de sombra
        # troca a cor de limpeza para branco
        self.clearColor = clearColor
        glClearColor(clearColor[0], clearColor[1], clearColor[2], 1)

        # transparência (imagens PNG)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.windowSize = pygame.display.get_surface().get_size()

        self.shadowsEnabled = False

    # ativa o passe de sombra (shadow mapping, seção 6.9)
    def enableShadows(self, shadowLight, strength=0.5,
                      resolution=[512, 512]):
        self.shadowsEnabled = True
        self.shadowObject = Shadow(shadowLight, strength=strength,
                                   resolution=resolution)

    def render(self, scene, camera, clearColor=True, clearDepth=True,
               renderTarget=None):

        # separa os objetos Mesh da cena
        descendantList = scene.getDescendantList()
        meshFilter = lambda x: isinstance(x, Mesh)
        meshList = list(filter(meshFilter, descendantList))

        # ---------------- passe de sombra ----------------
        if self.shadowsEnabled:

            # renderiza no framebuffer da sombra
            glBindFramebuffer(GL_FRAMEBUFFER,
                              self.shadowObject.renderTarget.framebufferRef)
            glViewport(0, 0, self.shadowObject.renderTarget.width,
                       self.shadowObject.renderTarget.height)

            # branco = "nada bloqueia a luz aqui"
            glClearColor(1, 1, 1, 1)
            glClear(GL_COLOR_BUFFER_BIT)
            glClear(GL_DEPTH_BUFFER_BIT)

            # tudo é desenhado com o DepthMaterial,
            # então o programa e as matrizes são definidos uma vez só
            glUseProgram(self.shadowObject.material.programRef)
            self.shadowObject.updateInternal()

            for mesh in meshList:

                if not mesh.visible:
                    continue

                # só malhas de triângulos projetam sombra
                if mesh.material.settings["drawStyle"] != GL_TRIANGLES:
                    continue

                glBindVertexArray(mesh.vaoRef)

                self.shadowObject.material.uniforms["modelMatrix"].data = \
                    mesh.getWorldMatrix()

                for varName, unifObj in \
                        self.shadowObject.material.uniforms.items():
                    unifObj.uploadData()

                glDrawArrays(GL_TRIANGLES, 0, mesh.geometry.vertexCount)

            # ajuste: restaura a cor de fundo da cena
            glClearColor(self.clearColor[0], self.clearColor[1],
                         self.clearColor[2], 1)

        # ---------------- passe principal ----------------

        # escolhe onde renderizar: janela ou render target
        if renderTarget is None:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glViewport(0, 0, self.windowSize[0], self.windowSize[1])
        else:
            glBindFramebuffer(GL_FRAMEBUFFER, renderTarget.framebufferRef)
            glViewport(0, 0, renderTarget.width, renderTarget.height)

        # limpa os buffers de cor e profundidade
        if clearColor:
            glClear(GL_COLOR_BUFFER_BIT)
        if clearDepth:
            glClear(GL_DEPTH_BUFFER_BIT)

        # atualiza a câmera (calcula a inversa)
        camera.updateViewMatrix()

        # luzes: os shaders esperam exatamente 4
        lightFilter = lambda x: isinstance(x, Light)
        lightList = list(filter(lightFilter, descendantList))
        while len(lightList) < 4:
            lightList.append(Light())

        for mesh in meshList:

            if not mesh.visible:
                continue

            glUseProgram(mesh.material.programRef)

            glBindVertexArray(mesh.vaoRef)

            # uniforms que vêm de fora do material
            mesh.material.uniforms["modelMatrix"].data = mesh.getWorldMatrix()
            mesh.material.uniforms["viewMatrix"].data = camera.viewMatrix
            mesh.material.uniforms["projectionMatrix"].data = \
                camera.projectionMatrix

            # materiais com luz recebem as 4 luzes
            if "light0" in mesh.material.uniforms.keys():
                for lightNumber in range(4):
                    lightName = "light" + str(lightNumber)
                    lightObject = lightList[lightNumber]
                    mesh.material.uniforms[lightName].data = lightObject

            # posição da câmera (luz especular)
            if "viewPosition" in mesh.material.uniforms.keys():
                mesh.material.uniforms["viewPosition"].data = \
                    camera.getWorldPosition()

            # dados da sombra, se o material usar
            if self.shadowsEnabled and \
                    "shadow0" in mesh.material.uniforms.keys():
                mesh.material.uniforms["shadow0"].data = self.shadowObject

            # envia todos os uniforms do material
            for variableName, uniformObject in mesh.material.uniforms.items():
                uniformObject.uploadData()

            # configurações de renderização
            mesh.material.updateRenderSettings()

            glDrawArrays(mesh.material.settings["drawStyle"], 0,
                         mesh.geometry.vertexCount)
