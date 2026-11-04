"""
Trabalho Prático - Computação Gráfica (UNIPAC 2026/02)
Temas: (2) Carrinho de carga  +  (20) Boneco de blocos

Cena: um pátio de carga.
  1. O carrinho chega pela pista com as rodas girando.
  2. Ao vê-lo, o boneco levanta o braço sinalizando "PARE"; o carrinho freia e para.
  3. O boneco gira o corpo, caminha até o carrinho e coloca a caixa na caçamba.
  4. O boneco recua, vira para a saída e acena "PODE IR".
  5. Só então o carrinho parte. O ciclo recomeça com uma nova caixa.

Framework: STEMKOSKI, L.; PASCALE, M. Developing Graphics Frameworks with
Python and OpenGL. CRC Press, 2022. As pastas core/, geometry/, material/,
light/ e extras/ do livro devem estar ao lado deste arquivo.
"""

import math
import os
import pygame

from core.base import Base
from core.renderer import Renderer
from core.scene import Scene
from core.camera import Camera
from core.mesh import Mesh
from core.group import Group
from core.texture import Texture
from core.matrix import Matrix
from geometry.boxGeometry import BoxGeometry
from geometry.cylinderGeometry import CylinderGeometry
from geometry.rectangleGeometry import RectangleGeometry
from light.ambientLight import AmbientLight
from light.directionalLight import DirectionalLight
from material.lambertMaterial import LambertMaterial
from extras.movementRig import MovementRig


# ----------------------------------------------------------------------
# Constantes da cena (unidades do mundo)
# ----------------------------------------------------------------------
LARGURA_TELA, ALTURA_TELA = 1024, 768
TITULO = "Patio de Carga - Carrinho + Boneco de Blocos"

# Carrinho
RAIO_RODA = 0.25
Y_CAIXA_NA_CACAMBA = 0.775        # centro da caixa apoiada no piso da caçamba
X_INICIO = -4.5                   # onde o carrinho surge
X_SINAL = -2.5                    # posição em que o boneco sinaliza "pare"
X_PARADA = 0.0                    # posição de entrega
X_FIM = 4.5                       # onde o carrinho termina o percurso
VEL_CARRINHO = 1.5                # unidades por segundo
# Frenagem com desaceleração constante: x(q) = x0 + L(2q - q^2).
# A duração é escolhida para a velocidade inicial ser igual a VEL_CARRINHO.
DUR_FRENAGEM = 2 * (X_PARADA - X_SINAL) / VEL_CARRINHO
DUR_PARTIDA = 3.0

# Boneco
X_BONECO = 0.0
Y_OMBRO = 1.3
DIST_OMBRO_CAIXA = 0.85
ANG_SEGURAR = 0.35                # braço levemente à frente segurando a caixa
ANG_ERGUER = 1.35                 # caixa erguida acima da parede da caçamba
# Ângulo do braço que leva a caixa exatamente até a altura da caçamba
ANG_ENTREGA = math.acos((Y_OMBRO - Y_CAIXA_NA_CACAMBA) / DIST_OMBRO_CAIXA)
Z_BONECO_LONGE = -1.8
Z_BONECO_PERTO = -DIST_OMBRO_CAIXA * math.sin(ANG_ENTREGA)
OLHA_X_NEG = -math.pi / 2         # olhando para onde o carrinho vem
OLHA_Z = 0.0                      # olhando para o carrinho
OLHA_X_POS = math.pi / 2          # olhando para a saída

# Sequência de etapas (máquina de estados)
PROXIMA_ETAPA = {
    "CHEGANDO": "SINAL_PARE",
    "SINAL_PARE": "VIRANDO",
    "VIRANDO": "APROXIMANDO",
    "APROXIMANDO": "ENTREGANDO",
    "ENTREGANDO": "RECUANDO",
    "RECUANDO": "LIBERANDO",
    "LIBERANDO": "PARTINDO",
}


# ----------------------------------------------------------------------
# Funções auxiliares
# ----------------------------------------------------------------------
def suave(p):
    """Smoothstep: 0 -> 1 com início e fim suaves (p é limitado a [0, 1])."""
    p = max(0.0, min(1.0, p))
    return p * p * (3 - 2 * p)


def lerp(a, b, p):
    return a + (b - a) * p


def envelope(p):
    """0 nas pontas e 1 no meio; usado para o balanço das pernas."""
    return math.sin(math.pi * max(0.0, min(1.0, p)))


def set_pose(obj, pos, rx=0.0, ry=0.0, rz=0.0):
    """Redefine a matriz local do objeto: translação seguida de rotações
    (Y, depois X, depois Z) em coordenadas locais."""
    obj.transform = Matrix.makeIdentity()
    obj.setPosition(pos)
    if ry:
        obj.rotateY(ry)
    if rx:
        obj.rotateX(rx)
    if rz:
        obj.rotateZ(rz)


def novo_material(cor=None, textura=None):
    """Material Lambert (sensível à luz) que também recebe sombra."""
    if textura is not None:
        return LambertMaterial(texture=textura, useShadow=True)
    return LambertMaterial(properties={"baseColor": cor}, useShadow=True)


def bloco(largura, altura, profundidade, material, posicao):
    malha = Mesh(BoxGeometry(largura, altura, profundidade), material)
    malha.setPosition(posicao)
    return malha


# ----------------------------------------------------------------------
# Aplicação
# ----------------------------------------------------------------------
class CenaPatioDeCarga(Base):

    def initialize(self):
        pygame.display.set_caption(TITULO)

        self.renderer = Renderer(clearColor=[0.55, 0.75, 0.95])
        self.scene = Scene()
        self.camera = Camera(aspectRatio=LARGURA_TELA / ALTURA_TELA)

        self.criar_iluminacao()
        self.criar_ambiente()
        self.criar_carrinho()
        self.criar_boneco()
        self.criar_camera()

        self.pausado = False
        self.reiniciar()

        print("Controles:")
        print("  W/A/S/D  mover câmera    R/F  subir/descer")
        print("  Q/E      girar câmera    T/G  olhar cima/baixo")
        print("  P        pausar/retomar  Z    reiniciar animação")

    # ------------------------------------------------------------------
    # Construção da cena
    # ------------------------------------------------------------------
    def criar_iluminacao(self):
        self.scene.add(AmbientLight(color=[0.35, 0.35, 0.35]))

        # Luz direcional (como o sol). A posição só importa para a câmera
        # de sombra; a iluminação usa apenas a direção.
        # Vem de cima e da direita, um pouco do lado da câmera: as sombras
        # caem à esquerda dos objetos, onde ficam visíveis.
        self.luz = DirectionalLight(color=[0.8, 0.8, 0.8],
                                    direction=[-1.2, -1.5, -0.5])
        # O eixo da luz atinge o chão na origem, então a câmera de sombra
        # (ortográfica, 10 x 10 unidades) cobre todo o percurso do carrinho.
        self.luz.setPosition([3.6, 4.5, 1.5])
        self.scene.add(self.luz)

        # Shadow mapping (seção 6.9 do livro): a cena é renderizada do ponto
        # de vista da luz para um mapa de profundidade, depois comparada no
        # shader de cada superfície com useShadow = True.
        self.renderer.enableShadows(self.luz, strength=0.5,
                                    resolution=[2048, 2048])

    def criar_ambiente(self):
        # Chão com textura de imagem. O RectangleGeometry cria UVs de 0 a 1;
        # multiplicamos por 8 para a imagem se repetir (wrap = GL_REPEAT).
        textura_chao = Texture("images/chao_concreto.png")
        geo_chao = RectangleGeometry(30, 30)
        uv = geo_chao.attributes["vertexUV"]
        uv.data = [[u * 8, v * 8] for (u, v) in uv.data]
        uv.uploadData()
        chao = Mesh(geo_chao, novo_material(textura=textura_chao))
        chao.rotateX(-math.pi / 2)
        self.scene.add(chao)

        # Faixas amarelas da pista e linha de parada
        amarelo = novo_material([0.95, 0.8, 0.1])
        branco = novo_material([0.95, 0.95, 0.95])
        self.scene.add(bloco(12, 0.01, 0.06, amarelo, [0, 0.005, 0.85]))
        self.scene.add(bloco(12, 0.01, 0.06, amarelo, [0, 0.005, -0.85]))
        self.scene.add(bloco(0.08, 0.01, 1.7, branco, [X_PARADA + 1.45, 0.006, 0]))

        # Pilha de caixas decorativas: mesma geometria, escalas diferentes
        self.textura_caixa = Texture("images/caixa_madeira.png")
        self.material_caixa = novo_material(textura=self.textura_caixa)
        for (x, y, z, escala, giro) in [
            (-3.2, 0.375, -2.6, 2.5, 0.2),
            (-2.35, 0.30, -2.7, 2.0, -0.3),
            (-3.2, 0.975, -2.6, 1.5, 0.6),
        ]:
            caixa = Mesh(BoxGeometry(0.3, 0.3, 0.3), self.material_caixa)
            caixa.setPosition([x, y, z])
            caixa.rotateY(giro)
            caixa.scale(escala)
            self.scene.add(caixa)

    def criar_carrinho(self):
        """Hierarquia: carrinho -> carroceria, cabine e pivôs das rodas."""
        self.carrinho = Group()
        laranja = novo_material([0.95, 0.55, 0.1])
        escuro = novo_material([0.15, 0.15, 0.18])
        cinza = novo_material([0.7, 0.7, 0.72])
        vidro = novo_material([0.3, 0.5, 0.7])

        # Chassi
        self.carrinho.add(bloco(2.1, 0.1, 0.8, escuro, [0.25, 0.42, 0]))
        # Caçamba: piso + 4 paredes
        self.carrinho.add(bloco(1.6, 0.15, 1.0, laranja, [0, 0.55, 0]))
        self.carrinho.add(bloco(0.08, 0.3, 1.0, laranja, [-0.76, 0.775, 0]))
        self.carrinho.add(bloco(0.08, 0.3, 1.0, laranja, [0.76, 0.775, 0]))
        self.carrinho.add(bloco(1.6, 0.3, 0.08, laranja, [0, 0.775, -0.46]))
        self.carrinho.add(bloco(1.6, 0.3, 0.08, laranja, [0, 0.775, 0.46]))
        # Cabine na frente (+X) e para-brisa
        self.carrinho.add(bloco(0.5, 0.6, 0.9, laranja, [1.05, 0.75, 0]))
        self.carrinho.add(bloco(0.02, 0.3, 0.7, vidro, [1.31, 0.85, 0]))

        # Rodas: cada uma tem um pivô (Group) que gira em Z.
        # O cilindro do livro tem eixo em Y; rotateX(90°) deixa o eixo em Z.
        self.rodas = []
        self.pos_rodas = []
        for (x, z) in [(-0.55, 0.55), (-0.55, -0.55), (0.95, 0.55), (0.95, -0.55)]:
            pivo = Group()
            pneu = Mesh(CylinderGeometry(RAIO_RODA, 0.12, 24, 1, True), escuro)
            pneu.rotateX(math.pi / 2)
            pivo.add(pneu)
            # Calota em barra: torna a rotação da roda visível
            pivo.add(bloco(0.36, 0.06, 0.13, cinza, [0, 0, 0]))
            self.carrinho.add(pivo)
            self.rodas.append(pivo)
            self.pos_rodas.append([x, RAIO_RODA, z])

        self.scene.add(self.carrinho)

    def criar_boneco(self):
        """Hierarquia: boneco -> tronco, cabeça, pivôs das pernas e ombros;
        a caixa é filha do ombro de carga enquanto está na mão."""
        self.boneco = Group()
        azul = novo_material([0.2, 0.45, 0.85])
        pele = novo_material([0.95, 0.8, 0.3])
        calca = novo_material([0.15, 0.2, 0.4])
        preto = novo_material([0.05, 0.05, 0.05])
        capacete = novo_material([0.95, 0.5, 0.05])

        self.boneco.add(bloco(0.6, 0.8, 0.3, azul, [0, 1.0, 0]))           # tronco
        self.boneco.add(bloco(0.4, 0.4, 0.4, pele, [0, 1.62, 0]))          # cabeça
        self.boneco.add(bloco(0.08, 0.08, 0.02, preto, [-0.1, 1.67, 0.205]))
        self.boneco.add(bloco(0.08, 0.08, 0.02, preto, [0.1, 1.67, 0.205]))
        self.boneco.add(bloco(0.46, 0.12, 0.46, capacete, [0, 1.88, 0]))  # capacete

        # Pernas: pivô no quadril (y = 0.6)
        self.perna_esq = Group()
        self.perna_esq.add(bloco(0.22, 0.6, 0.25, calca, [0, -0.3, 0]))
        self.perna_dir = Group()
        self.perna_dir.add(bloco(0.22, 0.6, 0.25, calca, [0, -0.3, 0]))

        # Braços: pivô no ombro; a malha fica pendurada para baixo
        self.ombro_sinal = Group()
        self.ombro_sinal.add(bloco(0.15, 0.7, 0.15, pele, [0, -0.35, 0]))
        self.ombro_carga = Group()
        self.ombro_carga.add(bloco(0.15, 0.7, 0.15, pele, [0, -0.35, 0]))

        # Caixa carregada (filha do ombro de carga)
        self.caixa = Mesh(BoxGeometry(0.3, 0.3, 0.3), self.material_caixa)
        self.ombro_carga.add(self.caixa)
        self.caixa_no_carrinho = False

        for parte in (self.perna_esq, self.perna_dir, self.ombro_sinal, self.ombro_carga):
            self.boneco.add(parte)
        self.scene.add(self.boneco)

    def criar_camera(self):
        self.rig = MovementRig(unitsPerSecond=2, degreesPerSecond=60)
        self.rig.add(self.camera)
        self.rig.setPosition([0, 2.4, 5.2])
        self.camera.rotateX(-0.3)
        self.scene.add(self.rig)

    # ------------------------------------------------------------------
    # Máquina de estados da animação
    # ------------------------------------------------------------------
    def reiniciar(self):
        if self.caixa_no_carrinho:
            self.pegar_nova_caixa()
        self.x_carrinho = X_INICIO
        self.giro_rodas = 0.0
        self.z_boneco = Z_BONECO_LONGE
        self.rot_boneco = OLHA_X_NEG
        self.a_sinal = 0.0
        self.a_carga = ANG_SEGURAR
        self.passo = 0.0
        self.entrar("CHEGANDO")
        self.aplicar_pose()

    def entrar(self, etapa):
        """Começa uma etapa guardando os valores iniciais para interpolar."""
        self.etapa = etapa
        self.t = 0.0
        self.ini = {
            "x": self.x_carrinho, "z": self.z_boneco, "rot": self.rot_boneco,
            "a_sinal": self.a_sinal, "a_carga": self.a_carga,
        }
        print(f"[etapa] {etapa}")

    def animar(self, dt):
        """Avança a animação em dt segundos (dt = 0 quando pausado),
        então a velocidade não depende da taxa de quadros."""
        self.t += dt
        t, ini, e = self.t, self.ini, self.etapa
        x_antes = self.x_carrinho
        self.passo = 0.0
        fim = False

        if e == "CHEGANDO":
            # Velocidade constante até o ponto em que o boneco o vê
            self.x_carrinho = min(self.x_carrinho + VEL_CARRINHO * dt, X_SINAL)
            fim = self.x_carrinho >= X_SINAL

        elif e == "SINAL_PARE":
            # Boneco ergue o braço; o carrinho responde freando até parar
            self.a_sinal = lerp(ini["a_sinal"], math.pi / 2, suave(t / 0.6))
            q = min(t / DUR_FRENAGEM, 1.0)
            self.x_carrinho = X_SINAL + (X_PARADA - X_SINAL) * (2 * q - q * q)
            fim = q >= 1.0

        elif e == "VIRANDO":
            # Carrinho parado: boneco baixa o braço, gira o corpo
            # e ergue a caixa acima da parede da caçamba
            q = suave(t / 1.0)
            self.rot_boneco = lerp(ini["rot"], OLHA_Z, q)
            self.a_sinal = lerp(ini["a_sinal"], 0.0, q)
            self.a_carga = lerp(ini["a_carga"], ANG_ERGUER, q)
            fim = t >= 1.0

        elif e == "APROXIMANDO":
            self.z_boneco = lerp(ini["z"], Z_BONECO_PERTO, suave(t / 1.0))
            self.passo = 0.5 * math.sin(t * 4 * math.pi) * envelope(t / 1.0)
            fim = t >= 1.0

        elif e == "ENTREGANDO":
            self.a_carga = lerp(ini["a_carga"], ANG_ENTREGA, suave(t / 1.2))
            fim = t >= 1.2

        elif e == "RECUANDO":
            # 1) levanta a mão acima da parede; 2) recua; 3) baixa o braço
            if t < 0.4:
                self.a_carga = lerp(ini["a_carga"], ANG_ERGUER, suave(t / 0.4))
            else:
                self.a_carga = lerp(ANG_ERGUER, 0.0, suave((t - 0.8) / 0.8))
            q = (t - 0.4) / 1.2
            self.z_boneco = lerp(ini["z"], Z_BONECO_LONGE, suave(q))
            self.passo = 0.5 * math.sin((t - 0.4) * 4 * math.pi) * envelope(q)
            fim = t >= 1.6

        elif e == "LIBERANDO":
            # Vira para a saída e acena "pode ir"
            self.rot_boneco = lerp(ini["rot"], OLHA_X_POS, suave(t / 0.6))
            self.a_sinal = 1.4 * suave(t / 0.5)
            if t > 0.5:
                self.a_sinal += 0.35 * math.sin(12 * (t - 0.5))
            fim = t >= 1.6

        elif e == "PARTINDO":
            # Só agora o carrinho parte, acelerando
            q = min(t / DUR_PARTIDA, 1.0)
            self.x_carrinho = X_PARADA + (X_FIM - X_PARADA) * q * q
            self.a_sinal = lerp(ini["a_sinal"], 0.0, suave(t / 0.5))
            self.rot_boneco = lerp(ini["rot"], OLHA_X_NEG, suave((t - 1.5) / 1.5))
            fim = q >= 1.0

        # Rodas: ângulo = distância percorrida / raio (rolamento sem deslizar)
        self.giro_rodas -= (self.x_carrinho - x_antes) / RAIO_RODA
        self.aplicar_pose()

        if fim:
            if e == "ENTREGANDO":
                self.soltar_caixa()
            if e == "PARTINDO":
                self.reiniciar()
                return
            self.entrar(PROXIMA_ETAPA[e])

    def aplicar_pose(self):
        """Converte o estado atual em matrizes locais de cada parte."""
        set_pose(self.carrinho, [self.x_carrinho, 0, 0])
        for pivo, pos in zip(self.rodas, self.pos_rodas):
            set_pose(pivo, pos, rz=self.giro_rodas)

        set_pose(self.boneco, [X_BONECO, 0, self.z_boneco], ry=self.rot_boneco)
        set_pose(self.perna_esq, [-0.15, 0.6, 0], rx=self.passo)
        set_pose(self.perna_dir, [0.15, 0.6, 0], rx=-self.passo)
        # Ângulo negativo em X leva o braço para a frente (+Z local)
        set_pose(self.ombro_sinal, [-0.4, Y_OMBRO, 0], rx=-self.a_sinal)
        set_pose(self.ombro_carga, [0.4, Y_OMBRO, 0], rx=-self.a_carga)
        if not self.caixa_no_carrinho:
            # Rotação oposta à do braço mantém a caixa nivelada
            set_pose(self.caixa, [0, -DIST_OMBRO_CAIXA, 0], rx=self.a_carga)

    def soltar_caixa(self):
        """Troca o pai da caixa: do ombro do boneco para o carrinho."""
        wx, wy, wz = self.caixa.getWorldPosition()
        self.ombro_carga.remove(self.caixa)
        self.carrinho.add(self.caixa)
        set_pose(self.caixa, [wx - self.x_carrinho, Y_CAIXA_NA_CACAMBA, wz])
        self.caixa_no_carrinho = True

    def pegar_nova_caixa(self):
        self.carrinho.remove(self.caixa)
        self.ombro_carga.add(self.caixa)
        self.caixa_no_carrinho = False

    # ------------------------------------------------------------------
    # Laço principal
    # ------------------------------------------------------------------
    def update(self):
        if self.input.isKeyDown("p"):
            self.pausado = not self.pausado
            sufixo = "  [PAUSADO]" if self.pausado else ""
            pygame.display.set_caption(TITULO + sufixo)
        if self.input.isKeyDown("z"):
            self.reiniciar()

        # Pausa congela só a animação; câmera e renderização continuam
        dt_animacao = 0.0 if self.pausado else self.deltaTime
        self.animar(dt_animacao)

        self.rig.update(self.input, self.deltaTime)
        self.renderer.render(self.scene, self.camera)


if __name__ == "__main__":
    # Garante que a pasta images/ seja encontrada, de onde quer que o
    # programa seja executado (PyCharm, terminal etc.)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    CenaPatioDeCarga(screenSize=[LARGURA_TELA, ALTURA_TELA]).run()
