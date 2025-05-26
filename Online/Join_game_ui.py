import pygame
import threading
from UI_tools.BaseUi import BaseUI
from Online.Client import Client
from Online.Server import ServerManager  
from Editor.Square_selector.SquareSelectorUi import SquareSelectorUi


class JoinGameUI(BaseUI):
    def __init__(self, title="Join Game"):
        super().__init__(title)
        self.title_font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        self.input_font = pygame.font.SysFont(None, 32)

        self.ip_text = "127.0.0.1"
        self.ip_active = False
        self.cursor_visible = True
        self.cursor_timer = 0

        self.connection_status = ""
        self.connection_color = (255, 255, 255)

        self.title_surface = self.title_font.render("Join Game", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 100))

        self.ip_input_rect = pygame.Rect((self.get_width() - 400) // 2, self.get_height() // 2 - 50, 400, 50)
        self.connect_button_rect = pygame.Rect((self.get_width() - 200) // 2, self.ip_input_rect.bottom + 50, 200, 60)
        self.back_button_rect = pygame.Rect(20, 20, 120, 40)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN and self.ip_active:
                self.handle_text_input(event)

    def handle_click(self, pos):
        if self.back_button_rect.collidepoint(pos):
            self.running = False
        elif self.connect_button_rect.collidepoint(pos):
            self.try_connection()
        self.ip_active = self.ip_input_rect.collidepoint(pos)

    def handle_text_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.ip_text = self.ip_text[:-1]
        elif event.key == pygame.K_RETURN:
            self.try_connection()
        elif event.unicode.isdigit() or event.unicode == ".":
            if len(self.ip_text) < 15:
                self.ip_text += event.unicode

    def try_connection(self):
        if not self.ip_text.strip():
            self.connection_status = "Erreur: Adresse IP vide"
            self.connection_color = (255, 100, 100)
            return

        self.connection_status = "Connexion in progress..."
        self.connection_color = (255, 255, 100)

        threading.Thread(target=self.attempt_connection, daemon=True).start()

    def attempt_connection(self):
        sock = Client.connect_to_server(self.ip_text.strip(), 5000)
        if sock:
            self.connection_status = f"Connected to {self.ip_text}"
            self.connection_color = (100, 255, 100)
        else:
            self.connection_status = "Connexion lost"
            self.connection_color = (255, 100, 100)

    def update(self):
        self.cursor_timer += self.clock.get_time()
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self):
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        screen.blit(self.title_surface, self.title_rect)

        pygame.draw.rect(screen, (100, 100, 100) if self.ip_active else (70, 70, 70), self.ip_input_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.ip_input_rect, 2)
        text_surface = self.input_font.render(self.ip_text, True, (255, 255, 255))
        screen.blit(text_surface, (self.ip_input_rect.x + 10, self.ip_input_rect.y + 10))

        if self.ip_active and self.cursor_visible:
            cursor_x = self.ip_input_rect.x + 10 + text_surface.get_width() + 2
            pygame.draw.line(screen, (255, 255, 255), (cursor_x, self.ip_input_rect.y + 10), (cursor_x, self.ip_input_rect.y + 40), 2)

        pygame.draw.rect(screen, (70, 130, 180), self.connect_button_rect, border_radius=8)
        connect_text = self.button_font.render("Connect", True, (255, 255, 255))
        screen.blit(connect_text, connect_text.get_rect(center=self.connect_button_rect.center))

        pygame.draw.rect(screen, (70, 70, 70), self.back_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button_rect, 2)
        back_text = self.button_font.render("Retour", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(center=self.back_button_rect.center))

        if self.connection_status:
            status = self.button_font.render(self.connection_status, True, self.connection_color)
            screen.blit(status, status.get_rect(center=(self.get_width() // 2, self.connect_button_rect.bottom + 30)))