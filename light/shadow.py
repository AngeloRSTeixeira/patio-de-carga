from OpenGL.GL import *

from core.camera import Camera
from core.renderTarget import RenderTarget
from material.depthMaterial import DepthMaterial


class Shadow(object):
    """Objetos usados no shadow mapping (seção 6.9.2)."""

    def __init__(self, lightSource, strength=0.5, resolution=[512, 512],
                 cameraBounds=[-5, 5, -5, 5, 0, 20], bias=0.01):

        super().__init__()

        # deve ser uma luz direcional
        self.lightSource = lightSource

        # câmera que "vê" a cena do ponto de vista da luz
        # (ortográfica, porque os raios da luz são paralelos)
        self.camera = Camera()
        left, right, bottom, top, near, far = cameraBounds
        self.camera.setOrthographic(left, right, bottom, top, near, far)
        self.lightSource.add(self.camera)

        # alvo do passe de sombra: contém a textura de profundidade
        self.renderTarget = RenderTarget(
            resolution, properties={"wrap": GL_CLAMP_TO_BORDER})

        # só a profundidade é gravada na textura
        self.material = DepthMaterial()

        # controla o quanto a sombra escurece
        self.strength = strength

        # evita artefatos de arredondamento ("acne" de sombra)
        self.bias = bias

    def updateInternal(self):
        self.camera.updateViewMatrix()
        self.material.uniforms["viewMatrix"].data = self.camera.viewMatrix
        self.material.uniforms["projectionMatrix"].data = \
            self.camera.projectionMatrix
