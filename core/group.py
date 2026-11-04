from core.object3D import Object3D


class Group(Object3D):
    """Nó interno, usado para transformar várias partes juntas (seção 4.2.1)."""

    def __init__(self):
        super().__init__()
