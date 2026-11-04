from numpy.linalg import inv

from core.object3D import Object3D
from core.matrix import Matrix


class Camera(Object3D):
    """Câmera virtual: matriz de visão e de projeção (seções 4.2.2 e 5.8)."""

    def __init__(self, angleOfView=60, aspectRatio=1, near=0.1, far=1000):
        super().__init__()
        self.projectionMatrix = Matrix.makePerspective(
            angleOfView, aspectRatio, near, far)
        self.viewMatrix = Matrix.makeIdentity()

    # a matriz de visão é a inversa da transformação da câmera
    def updateViewMatrix(self):
        self.viewMatrix = inv(self.getWorldMatrix())

    def setPerspective(self, angleOfView=50, aspectRatio=1, near=0.1,
                       far=1000):
        self.projectionMatrix = Matrix.makePerspective(
            angleOfView, aspectRatio, near, far)

    def setOrthographic(self, left=-1, right=1, bottom=-1, top=1,
                        near=-1, far=1):
        self.projectionMatrix = Matrix.makeOrthographic(
            left, right, bottom, top, near, far)
