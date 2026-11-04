import pygame


class Input(object):
    """Eventos de teclado e de fechar a janela (seções 2.1 e 2.4.4)."""

    def __init__(self):

        # o usuário fechou a aplicação?
        self.quit = False

        # listas com o estado das teclas
        #   down, up: eventos discretos; duram uma iteração
        #   pressed: evento contínuo, entre down e up
        self.keyDownList = []
        self.keyPressedList = []
        self.keyUpList = []

    def update(self):

        # zera os estados discretos
        self.keyDownList = []
        self.keyUpList = []

        # percorre os eventos ocorridos desde a última verificação
        for event in pygame.event.get():

            # clicar no X da janela gera o evento QUIT
            if event.type == pygame.QUIT:
                self.quit = True

            # pega o nome da tecla e atualiza as listas
            if event.type == pygame.KEYDOWN:
                keyName = pygame.key.name(event.key)
                self.keyDownList.append(keyName)
                self.keyPressedList.append(keyName)
            if event.type == pygame.KEYUP:
                keyName = pygame.key.name(event.key)
                # ajuste: a tecla pode ter sido pressionada antes
                # de a janela receber o foco
                if keyName in self.keyPressedList:
                    self.keyPressedList.remove(keyName)
                self.keyUpList.append(keyName)

    # funções para consultar o estado das teclas
    def isKeyDown(self, keyCode):
        return keyCode in self.keyDownList

    def isKeyPressed(self, keyCode):
        return keyCode in self.keyPressedList

    def isKeyUp(self, keyCode):
        return keyCode in self.keyUpList
