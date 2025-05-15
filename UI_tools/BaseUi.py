import pygame

class BaseUI:
    def __init__(self, title="Katarenga"):
        pygame.init()

        self.__title = title
        self.__screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption(self.__title)

        display_info = pygame.display.Info()
        self.__width = display_info.current_w
        self.__height = display_info.current_h

        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.SysFont(None, 48)

    def get_screen(self):
        return self.__screen

    def get_width(self):
        return self.__width

    def get_height(self):
        return self.__height