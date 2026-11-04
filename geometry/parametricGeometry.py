import numpy

from geometry.geometry import Geometry


class ParametricGeometry(Geometry):
    """Superfície definida por uma função S(u, v)
    (seções 4.3.4, 5.2.4 e 6.3.4)."""

    def __init__(self, uStart, uEnd, uResolution,
                 vStart, vEnd, vResolution, surfaceFunction):
        super().__init__()

        # pontos da superfície
        deltaU = (uEnd - uStart) / uResolution
        deltaV = (vEnd - vStart) / vResolution
        positions = []
        for uIndex in range(uResolution + 1):
            vArray = []
            for vIndex in range(vResolution + 1):
                u = uStart + uIndex * deltaU
                v = vStart + vIndex * deltaV
                vArray.append(surfaceFunction(u, v))
            positions.append(vArray)

        # coordenadas de textura
        uvs = []
        for uIndex in range(uResolution + 1):
            vArray = []
            for vIndex in range(vResolution + 1):
                u = uIndex / uResolution
                v = vIndex / vResolution
                vArray.append([u, v])
            uvs.append(vArray)

        # normal a partir de três pontos (produto vetorial)
        def calcNormal(P0, P1, P2):
            v1 = numpy.array(P1) - numpy.array(P0)
            v2 = numpy.array(P2) - numpy.array(P0)
            normal = numpy.cross(v1, v2)
            length = numpy.linalg.norm(normal)
            # ajuste: evita divisão por zero em pontos degenerados
            if length < 1e-12:
                return [0, 0, 0]
            return list(normal / length)

        # normais de vértice: pontos muito próximos de P0
        vertexNormals = []
        for uIndex in range(uResolution + 1):
            vArray = []
            for vIndex in range(vResolution + 1):
                u = uStart + uIndex * deltaU
                v = vStart + vIndex * deltaV
                h = 0.0001
                P0 = surfaceFunction(u, v)
                P1 = surfaceFunction(u + h, v)
                P2 = surfaceFunction(u, v + h)
                vArray.append(calcNormal(P0, P1, P2))
            vertexNormals.append(vArray)

        # agrupa os dados em triângulos
        positionData = []
        colorData = []
        uvData = []
        vertexNormalData = []
        faceNormalData = []

        C1, C2, C3 = [1, 0, 0], [0, 1, 0], [0, 0, 1]
        C4, C5, C6 = [0, 1, 1], [1, 0, 1], [1, 1, 0]

        for xIndex in range(uResolution):
            for yIndex in range(vResolution):

                # posições
                pA = positions[xIndex + 0][yIndex + 0]
                pB = positions[xIndex + 1][yIndex + 0]
                pD = positions[xIndex + 0][yIndex + 1]
                pC = positions[xIndex + 1][yIndex + 1]
                positionData += [pA.copy(), pB.copy(), pC.copy(),
                                 pA.copy(), pC.copy(), pD.copy()]

                # cores
                colorData += [C1, C2, C3, C4, C5, C6]

                # coordenadas de textura
                uvA = uvs[xIndex + 0][yIndex + 0]
                uvB = uvs[xIndex + 1][yIndex + 0]
                uvD = uvs[xIndex + 0][yIndex + 1]
                uvC = uvs[xIndex + 1][yIndex + 1]
                uvData += [uvA, uvB, uvC, uvA, uvC, uvD]

                # normais de vértice
                nA = vertexNormals[xIndex + 0][yIndex + 0]
                nB = vertexNormals[xIndex + 1][yIndex + 0]
                nD = vertexNormals[xIndex + 0][yIndex + 1]
                nC = vertexNormals[xIndex + 1][yIndex + 1]
                vertexNormalData += [nA, nB, nC, nA, nC, nD]

                # normais de face
                fn0 = calcNormal(pA, pB, pC)
                fn1 = calcNormal(pA, pC, pD)
                faceNormalData += [fn0, fn0, fn0, fn1, fn1, fn1]

        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec3", "vertexColor", colorData)
        self.addAttribute("vec2", "vertexUV", uvData)
        self.addAttribute("vec3", "vertexNormal", vertexNormalData)
        self.addAttribute("vec3", "faceNormal", faceNormalData)
        self.countVertices()
