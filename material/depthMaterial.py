from material.material import Material


class DepthMaterial(Material):
    """Grava a profundidade de cada fragmento, vista da luz (seção 6.9.2)."""

    def __init__(self):

        vertexShaderCode = """
        in vec3 vertexPosition;
        uniform mat4 projectionMatrix;
        uniform mat4 viewMatrix;
        uniform mat4 modelMatrix;

        void main()
        {
            gl_Position = projectionMatrix * viewMatrix * modelMatrix
                          * vec4(vertexPosition, 1);
        }
        """

        fragmentShaderCode = """
        out vec4 fragColor;

        void main()
        {
            // gl_FragCoord.z guarda a profundidade (0 a 1)
            float z = gl_FragCoord.z;
            fragColor = vec4(z, z, z, 1);
        }
        """

        super().__init__(vertexShaderCode, fragmentShaderCode)
        self.locateUniforms()
