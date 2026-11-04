import pygame
import sys

from core.input import Input


class Base(object):
    """Janela, laço principal e controle de tempo (seções 2.1 e 2.4)."""

    def __init__(self, screenSize=[512, 512]):

        # inicializa todos os módulos do pygame
        pygame.init()
        # detalhes da renderização: buffer duplo + contexto OpenGL
        displayFlags = pygame.DOUBLEBUF | pygame.OPENGL
        # buffers para antialiasing (multisampling)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        # perfil "core" do OpenGL (versão 3.3) para compatibilidade
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        # cria e exibe a janela
        try:
            self.screen = pygame.display.set_mode(screenSize, displayFlags)
        except pygame.error:
            # ajuste: se a placa de vídeo não suportar antialiasing,
            # cria a janela sem ele
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 0)
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 0)
            self.screen = pygame.display.set_mode(screenSize, displayFlags)
        # texto da barra de título
        pygame.display.set_caption("Graphics Window")

        # o laço principal está ativo?
        self.running = True
        # gerencia dados e operações ligadas ao tempo
        self.clock = pygame.time.Clock()

        # gerencia a entrada do usuário
        self.input = Input()

        # segundos desde o início da aplicação
        self.time = 0
        # segundos desde o quadro anterior
        self.deltaTime = 0

    # implementado pela classe que estende Base
    def initialize(self):
        pass

    # implementado pela classe que estende Base
    def update(self):
        pass

    def run(self):

        ## inicialização ##
        self.initialize()

        ## laço principal ##
        while self.running:

            ## processa a entrada ##
            self.input.update()
            if self.input.quit:
                self.running = False

            # segundos desde a última iteração do laço
            self.deltaTime = self.clock.get_time() / 1000
            # tempo total de execução
            self.time += self.deltaTime

            ## atualiza ##
            self.update()

            ## renderiza ##
            # mostra a imagem na tela
            pygame.display.flip()

            # pausa se necessário para manter 60 FPS
            self.clock.tick(60)

        ## encerramento ##
        pygame.quit()
        sys.exit()
