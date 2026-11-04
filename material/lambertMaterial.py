from OpenGL.GL import *

from material.material import Material


class LambertMaterial(Material):
    """Iluminação difusa de Lambert, calculada por fragmento,
    com textura e sombra opcionais (seções 6.4.2 e 6.9.2)."""

    def __init__(self, texture=None, properties={}, useShadow=False):

        vertexShaderCode = """
        struct Shadow
        {
            // direção da luz que projeta a sombra
            vec3 lightDirection;
            // câmera que gera a textura de profundidade
            mat4 projectionMatrix;
            mat4 viewMatrix;
            // profundidades vistas pela câmera da sombra
            sampler2D depthTexture;
            // regiões na sombra são multiplicadas por (1 - strength)
            float strength;
            // reduz artefatos de precisão
            float bias;
        };

        uniform mat4 projectionMatrix;
        uniform mat4 viewMatrix;
        uniform mat4 modelMatrix;

        in vec3 vertexPosition;
        in vec2 vertexUV;
        in vec3 vertexNormal;

        out vec3 position;
        out vec2 UV;
        out vec3 normal;

        uniform bool useShadow;
        uniform Shadow shadow0;
        out vec3 shadowPosition0;

        void main()
        {
            gl_Position = projectionMatrix * viewMatrix * modelMatrix
                          * vec4(vertexPosition, 1);
            position = vec3( modelMatrix * vec4(vertexPosition, 1) );
            UV = vertexUV;
            normal = normalize( mat3(modelMatrix) * vertexNormal );

            // posição do vértice em relação à câmera da sombra
            if (useShadow)
            {
                vec4 temp0 = shadow0.projectionMatrix * shadow0.viewMatrix
                             * modelMatrix * vec4(vertexPosition, 1);
                shadowPosition0 = vec3( temp0 );
            }
        }
        """

        fragmentShaderCode = """
        struct Light
        {
            // 1 = AMBIENT, 2 = DIRECTIONAL, 3 = POINT
            int lightType;
            // usado por todas as luzes
            vec3 color;
            // usado pela luz direcional
            vec3 direction;
            // usados pela luz pontual
            vec3 position;
            vec3 attenuation;
        };

        uniform Light light0;
        uniform Light light1;
        uniform Light light2;
        uniform Light light3;

        vec3 lightCalc(Light light, vec3 pointPosition, vec3 pointNormal)
        {
            float ambient = 0;
            float diffuse = 0;
            float specular = 0;
            float attenuation = 1;
            vec3 lightDirection = vec3(0,0,0);

            if ( light.lightType == 1 )       // luz ambiente
            {
                ambient = 1;
            }
            else if ( light.lightType == 2 )  // luz direcional
            {
                lightDirection = normalize(light.direction);
            }
            else if ( light.lightType == 3 )  // luz pontual
            {
                lightDirection = normalize(pointPosition - light.position);
                float distance = length(light.position - pointPosition);
                attenuation = 1.0 / (light.attenuation[0]
                                   + light.attenuation[1] * distance
                                   + light.attenuation[2] * distance * distance);
            }

            if ( light.lightType > 1 )        // direcional ou pontual
            {
                pointNormal = normalize(pointNormal);
                // Lambert: cosseno do ângulo entre normal e luz
                diffuse = max( dot(pointNormal, -lightDirection), 0.0 );
                diffuse *= attenuation;
            }

            return light.color * (ambient + diffuse + specular);
        }

        struct Shadow
        {
            vec3 lightDirection;
            mat4 projectionMatrix;
            mat4 viewMatrix;
            sampler2D depthTexture;
            float strength;
            float bias;
        };

        uniform vec3 baseColor;
        uniform bool useTexture;
        // ajuste: o livro chama este sampler de "texture" e usa
        // texture2D(); no perfil core 3.3 o nome conflita com a
        // função texture() e texture2D() não existe
        uniform sampler2D textureSampler;

        uniform bool useShadow;
        uniform Shadow shadow0;
        in vec3 shadowPosition0;

        in vec3 position;
        in vec2 UV;
        in vec3 normal;
        out vec4 fragColor;

        void main()
        {
            vec4 color = vec4(baseColor, 1.0);
            if ( useTexture )
                color *= texture( textureSampler, UV );

            // efeito total das luzes na cor
            vec3 total = vec3(0,0,0);
            total += lightCalc( light0, position, normal );
            total += lightCalc( light1, position, normal );
            total += lightCalc( light2, position, normal );
            total += lightCalc( light3, position, normal );
            color *= vec4( total, 1 );

            if (useShadow)
            {
                // a superfície está virada para a luz?
                float cosAngle = dot( normalize(normal),
                                      -normalize(shadow0.lightDirection) );
                bool facingLight = (cosAngle > 0.01);

                // converte o intervalo [-1, 1] para [0, 1]
                // (coordenada UV e profundidade)
                vec3 shadowCoord = (shadowPosition0.xyz + 1.0) / 2.0;
                float closestDistanceToLight =
                    texture( shadow0.depthTexture, shadowCoord.xy ).r;
                float fragmentDistanceToLight = clamp(shadowCoord.z, 0, 1);

                // o fragmento está na sombra de outro objeto?
                bool inShadow = ( fragmentDistanceToLight >
                                  closestDistanceToLight + shadow0.bias );

                if (facingLight && inShadow)
                {
                    float s = 1.0 - shadow0.strength;
                    color *= vec4(s, s, s, 1);
                }
            }

            fragColor = color;
        }
        """

        super().__init__(vertexShaderCode, fragmentShaderCode)

        self.addUniform("vec3", "baseColor", [1.0, 1.0, 1.0])
        self.addUniform("Light", "light0", None)
        self.addUniform("Light", "light1", None)
        self.addUniform("Light", "light2", None)
        self.addUniform("Light", "light3", None)

        if texture is None:
            self.addUniform("bool", "useTexture", False)
        else:
            self.addUniform("bool", "useTexture", True)
            self.addUniform("sampler2D", "textureSampler",
                            [texture.textureRef, 1])

        if not useShadow:
            self.addUniform("bool", "useShadow", False)
        else:
            self.addUniform("bool", "useShadow", True)
            self.addUniform("Shadow", "shadow0", None)

        self.locateUniforms()

        # renderizar os dois lados?
        self.settings["doubleSide"] = True
        # renderizar como aramado?
        self.settings["wireframe"] = False
        # espessura da linha no modo aramado
        self.settings["lineWidth"] = 1

        self.setProperties(properties)

    def updateRenderSettings(self):

        if self.settings["doubleSide"]:
            glDisable(GL_CULL_FACE)
        else:
            glEnable(GL_CULL_FACE)

        if self.settings["wireframe"]:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # ajuste: no perfil core, larguras de linha diferentes de 1
        # podem gerar erro em alguns drivers
        if self.settings["lineWidth"] != 1:
            glLineWidth(self.settings["lineWidth"])
