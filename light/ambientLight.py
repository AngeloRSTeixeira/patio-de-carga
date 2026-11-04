from light.light import Light


class AmbientLight(Light):
    """Luz que ilumina todas as superfícies igualmente (seção 6.2)."""

    def __init__(self, color=[1, 1, 1]):
        super().__init__(Light.AMBIENT)
        self.color = color
